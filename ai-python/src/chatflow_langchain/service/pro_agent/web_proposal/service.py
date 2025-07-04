from src.logger.default_logger import logger
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.output_parsers import JsonOutputParser
import json
import docx
from langchain.chains.llm import LLMChain
from fastapi import status, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.chatflow_langchain.repositories.tool_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from src.chatflow_langchain.service.pro_agent.web_proposal.config import ChatHistoryConfig, WebProposalConfig
from src.chatflow_langchain.service.pro_agent.web_proposal.chat_prompt_factory import create_chat_prompt_proposal,create_chat_prompt_requirements,create_chat_prompt_company_summary
from src.chatflow_langchain.service.pro_agent.web_proposal.utils import web_scraping,ProposalDocument,parse_proposal_content,upload_doc_to_s3
import asyncio
from langchain_community.callbacks.manager import get_openai_callback
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
import os
from src.db.config import get_field_by_name
import pandas as pd
from src.chatflow_langchain.service.config.model_config_openai import OPENAIMODEL,DefaultOpenAIModelRepository
from datetime import datetime
from openai import RateLimitError,APIConnectionError,APITimeoutError,APIStatusError, NotFoundError
from src.chatflow_langchain.service.openai.image.utils import extract_error_message
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from src.gateway.openai_exceptions import LengthFinishReasonError,ContentFilterFinishReasonError
import gc

class WebProposalService:
    def __init__(self):
        self.llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
        self.thread_repo = ThreadRepostiory()
        self.chat_repository_history = CustomAIMongoDBChatMessageHistory()


    async def initilize_chat_input(self,chat_input=None):
        self.chat_input = chat_input
        self.url=self.chat_input.query
        self.company_id=chat_input.company_id
        self.thread_id=chat_input.thread_id
        self.thread_model=chat_input.threadmodel
        self.companymodel=chat_input.companymodel
        self.regenerated_flag=chat_input.isregenerated
        self.delay_chunk=chat_input.delay_chunk
        self.chat_session_id=chat_input.chat_session_id
        self.delay_chunk=chat_input.delay_chunk
        self.isregenerated=chat_input.isregenerated
        self.msgCredit=chat_input.msgCredit
        self.is_paid_user=chat_input.is_paid_user
        self.agent_info = chat_input.agent_extra_info
        doc = docx.Document(WebProposalConfig.TEMPLATE_PATH)
        self.proposal_doc = ProposalDocument(doc)
        
    async def scrape_url_content(self):
        try:
            self.url_content = await web_scraping(self.url)
            self.company_summary_task = asyncio.create_task(self.generate_summaries(self.url_content))
        except Exception as e:
            logger.info(f"Critical error in scrape_url_content: {e}")
            raise Exception(f"Failed to retrieve content from {self.url} with all provided User-Agents")

    async def generate_summaries(self,url_content):
        with get_openai_callback() as cb:
            self.summary_prompt = create_chat_prompt_company_summary()
            self.summary_chain=LLMChain(llm=self.llm,prompt= self.summary_prompt)
            self.business_summary = await self.summary_chain.ainvoke({
                                            'page_analysis': url_content, 
                                        })
        update_task = await self.async_initialize_and_update(self.thread_model,self.thread_id, cb, msgCredit=0,is_paid_user=self.is_paid_user) 
    
    async def initialize_llm(self):
        """
        Initializes the LLM with the specified API key and company model.

        Parameters
        ----------
        api_key_id : str, optional
            The API key ID used for decryption and initialization.
        companymodel : str, optional
            The company model configuration for the LLM.

        Exceptions
        ----------
        Logs an error if the initialization fails.
        """ 
        try:
            self.chat_repository_history = CustomAIMongoDBChatMessageHistory()
            self.api_key_id=DefaultOpenAIModelRepository(self.company_id,self.companymodel).get_default_model_key()
            self.llm_apikey_decrypt_service.initialization(self.api_key_id, self.companymodel)
            self.bot_data = self.llm_apikey_decrypt_service.bot_data
            self.model_name = OPENAIMODEL.MODEL_VERSIONS[self.llm_apikey_decrypt_service.model_name]
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=1,
                api_key=self.llm_apikey_decrypt_service.decrypt(),
                streaming=True,
                verbose=False,
                stream_usage=True
            )
            self.llm_non_stream = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.llm_apikey_decrypt_service.extra_config.get('temperature'),
                api_key=self.llm_apikey_decrypt_service.decrypt(),
                streaming=False,
                verbose=False
            )
            self.llm_sum_memory = ChatOpenAI(
                model_name=self.model_name,
                temperature=self.llm_apikey_decrypt_service.extra_config.get('temperature'),
                api_key=self.llm_apikey_decrypt_service.decrypt(),
                streaming=False,
                verbose=False
            )
        except Exception as e:
            logger.error(
                f"Failed to initialize LLM: {e}",
                extra={"tags": {"method": "StreamingDocumentedChatService.initialize_llm"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")

    async def initialize_repository(self):
        """
        Initializes the chat history repository for data storage.

        Parameters
        ----------
        chat_session_id : str, optional
            The chat session ID for the repository.
        collection_name : str, optional
            The collection name for the repository.

        Exceptions
        ----------
        Logs an error if the repository initialization fails.
        """
        try:
            self.chat_repository_history.initialize(
                chat_session_id=self.chat_session_id,
                collection_name=self.thread_model,
                regenerated_flag=self.isregenerated,
                thread_id=self.thread_id
            )
            self.initialize_memory()
        except Exception as e:
            logger.error(
                f"Failed to initalize repository: {e}",
                extra={"tags": {"method": "WebProposalService.initialize_repository"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initalize repository: {e}")

    def initialize_memory(self):
        """
        Sets up the memory component using ConversationSummaryBufferMemory.

        Exceptions
        ----------
        Logs an error if the memory initialization fails.
        """
        try:
            self.memory = ConversationSummaryBufferMemory(
                memory_key="chat_history",
                input_key="question",
                output_key="answer",
                llm=self.llm_sum_memory,
                max_token_limit=ChatHistoryConfig.MAX_TOKEN_LIMIT,
                return_messages=True,
                chat_memory=self.chat_repository_history
            )
            self.memory.moving_summary_buffer = self.chat_repository_history.memory_buffer
        except Exception as e:
            logger.error(
                f"Failed to initalize memory: {e}",
                extra={"tags": {"method": "WebProposalService.initialize_memory"}}
            )
            
    async def create_chain(self):
        """
        Creates the prompt for the LLM using the scraped content.

        Returns
        -------
        str
            The prompt for the LLM.
        """
        try:
            self.prompt = create_chat_prompt_proposal()
            self.prompt_requirements = create_chat_prompt_requirements()
            self.llm_chain_proposal = LLMChain(llm=self.llm,prompt=self.prompt)
            self.llm_chain_requirements = LLMChain(llm=self.llm,prompt=self.prompt_requirements)
        except Exception as e:
            logger.error(f"Failed to create chain: {e}",
                         extra={"tags": {"method": "WebProposalService.create_chain"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create chain: {e}") 
    
    async def async_initialize_and_update(self,chat_collection_name, thread_id,cb,msgCredit,is_paid_user):
        try:
            self.thread_repo.initialization(thread_id=thread_id, collection_name=chat_collection_name)       

            # thread token update
            self.thread_repo.update_token_usage(cb)
            if is_paid_user:
                self.thread_repo.update_credits(msgCredit=msgCredit)
            update_responseModel = {
                "$set": {
                    "responseModel":OPENAIMODEL.GPT_4_1,
                    "model":self.bot_data
                }}
            self.thread_repo.update_fields(data=update_responseModel)
            logger.info("Database successfully stored response",
                extra={"tags":{"method": "WebProposalService.async_initialize_and_update"}})
        except Exception as e:
            logger.error(f"Error occurred during async initialization and update: {e}",
                         extra={"tags": {"method": "WebProposalService.async_initialize_and_update"}})
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Failed to initialize and update chat thread: {e}")
        
    async def run_chain(self):
                # Format dates first, before any other processing
        try:
            await self.company_summary_task
            # Convert dates using datetime

            discussion_date = datetime.strptime(self.agent_info['discussionDate'], '%Y-%m-%d')
            submission_date = datetime.strptime(self.agent_info['submissionDate'], '%Y-%m-%d')
            
            # Format dates to the desired format
            self.agent_info['discussionDate'] = discussion_date.strftime('%B %d, %Y')
            self.agent_info['submissionDate'] = submission_date.strftime('%B %d, %Y')
            
            # print(f"Formatted Discussion Date: {submission_details['discussionDate']}")
            # print(f"Formatted Submission Date: {submission_details['submissionDate']}")

            with get_openai_callback() as cb:
                proposal_content = self.llm_chain_proposal.invoke({'client_name': self.agent_info['clientName'],'project_name': self.agent_info['projectName'],'project_description': self.agent_info['projectDescription']})
                proposal_data = parse_proposal_content(proposal_content['text'])
                requirements_content = self.llm_chain_requirements.invoke({'project_name':proposal_data["project_overview"]['projectName'],'project_description':self.agent_info['projectDescription']})
                requirement_summary = json.loads(requirements_content['text'])
            # Add the requirement summary to project_overview
            if proposal_data and "project_overview" in proposal_data:
                proposal_data["project_overview"].update({
                    "projectSummary": requirement_summary.get("projectSummary", ""),
                    "userExperience": requirement_summary.get("userExperience", ""),
                    "designDevelopment": requirement_summary.get("designDevelopment", "")
                })
            core_costs = [
                float(str(proposal_data['core_budget'][key]).replace('$', '').replace(',', ''))
                for key in ['researchCost', 'designCost', 'frontEndCost', 'backEndCost', 'qaTestingCost']
            ]
            total_core_cost = sum(core_costs)
            proposal_data['core_budget']['totalCoreCost'] = total_core_cost

            # Calculate totalRecommandedCost
            addon_costs = [
                float(str(proposal_data['recommended_addons'][key]).replace('$', '').replace(',', ''))
                for key in ['userTestingCost', 'maintenanceCost']
            ]
            total_recommended_cost = sum(addon_costs)
            proposal_data['recommended_addons']['totalRecommandedCost'] = total_recommended_cost

            # Calculate total project cost
            total_project_cost = total_core_cost + total_recommended_cost
            proposal_data['total_cost'] = {
                "totalProjectCost": total_project_cost
            }
            proposal_data['submission_details'] = self.agent_info
            proposal_data['userCompanySummary'] = self.business_summary.get('text')


            self.proposal_doc.replace_placeholders(proposal_data)   
            self.file_url = await upload_doc_to_s3(self.proposal_doc.doc)
            update_task = await self.async_initialize_and_update(self.thread_model,self.thread_id, cb, msgCredit=self.msgCredit,is_paid_user=self.is_paid_user)
            self.final_ai_message = f"## 🎉 Proposal Ready\nYour web project proposal has been successfully generated.\n\n👉 [Download Your Proposal Here]({self.file_url})"
            self.chat_repository_history.add_ai_message_kwargs(
                        message=self.final_ai_message,
                        thread_id=self.thread_id,
                        proposal_data=proposal_data
                        )
            self.chat_repository_history.add_message_system(
                message=self.memory.moving_summary_buffer,
                thread_id=self.thread_id)
            
            # Yield the markdown content
            yield f"data: {self.final_ai_message.encode('utf-8')}\n\n", 200
            await asyncio.sleep(self.delay_chunk + 0.03) 
        except NotFoundError as e:
                error_content,error_code = extract_error_message(str(e))
                if error_code not in OPENAI_MESSAGES_CONFIG:
                    logger.warning(
                        f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "WebProposalAgent.run_chain.NotFoundError"}})
                else:
                    logger.error(
                        f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "WebProposalAgent.run_chain.NotFoundError"}})
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.add_message_openai(error_code)

                self.llm_apikey_decrypt_service.initialization(self.api_key_id,"companymodel")
                self.llm_apikey_decrypt_service.update_deprecated_status(True)
                content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except RateLimitError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "WebProposalAgent.run_chain.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "WebProposalAgent.run_chain.RateLimitError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_openai(error_code)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS
    
        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in OPENAI_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "WebProposalAgent.run_chain.APIStatusError"}})
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.add_message_openai("common_response")
                content = OPENAI_MESSAGES_CONFIG.get("common_response")
                error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "WebProposalAgent.run_chain.APIStatusError"}})
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.add_message_openai(error_code)
                content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except LengthFinishReasonError as e:
            logger.error(
                f"OpenAI Length Finish Reason Error: {e}",
                extra={"tags": {"method": "WebProposalAgent.run_chain.LengthFinishReasonError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except ContentFilterFinishReasonError as e:
            logger.error(
                f"OpenAI Content Filter Error: {e}",
                extra={"tags": {"method": "WebProposalAgent.run_chain.ContentFilterFinishReasonError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_openai("content_filter_issue")
            content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
        except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "WebProposalAgent.run_chain.APITimeoutError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_openai("request_time_out")
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "WebProposalAgent.run_chain.APIConnectionError"}})
            self.thread_repo.initialization(self.thread_id, self.thread_model)
            self.thread_repo.add_message_openai("connection_error")
            content = OPENAI_MESSAGES_CONFIG.get("connection_error", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except Exception as e:
            try:
                error_content,error_code = extract_error_message(str(e))
                if error_code not in OPENAI_MESSAGES_CONFIG:
                    logger.warning(
                        f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "WebProposalAgent.run_chain.Exception_Try"}})
                else:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "WebProposalAgent.run_chain.Exception_Try"}})
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.add_message_openai(error_code)
                content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
            except Exception as e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {e}",
                    extra={"tags": {"method": "WebProposalAgent.run_chain.Exception_Except"}})
                self.thread_repo.initialization(self.thread_id, self.thread_model)
                self.thread_repo.add_message_openai("common_response")
                content = OPENAI_MESSAGES_CONFIG.get("common_response")
                yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("dev_message"), "data": content}), status.HTTP_400_BAD_REQUEST

        finally:
                self.cleanup()

    def cleanup(self):
        """
        Cleans up any resources or state associated with the service.
        """
        try:
            # List of attributes to clean up
            attributes = [
                'llm',
                'llm_non_stream',
                'llm_sum_memory',
                'memory',
                'llm_chain_proposal',
                'llm_chain_requirements',
                'summary_chain',
                'business_summary',
                'inputs',
                'url_content',
                'chat_repository_history',
                'scraped_content',
                'agent_extra_info',
                'company_summary_task',
                'proposal_doc',
                'cost_calculator'  # Add this if it's used in the service
            ]

            cleaned_up = []
            for attr in attributes:
                if hasattr(self, attr):
                    delattr(self, attr)
                    cleaned_up.append(attr)
            
            # Log the cleanup process
            if cleaned_up:
                logger.info(f"Successfully cleaned up: {', '.join(cleaned_up)}.")
            
            gc.collect()  # Force garbage collection to free memory

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "WebProposalAgent.cleanup"}}
            )