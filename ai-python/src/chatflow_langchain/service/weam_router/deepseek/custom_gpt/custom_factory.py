from fastapi import HTTPException
from src.logger.default_logger import logger
from src.chatflow_langchain.service.weam_router.deepseek.custom_gpt.doc.rag_conversation import WeamDeepSeekCustomGPTDocChatService
from src.chatflow_langchain.service.weam_router.deepseek.custom_gpt.simple_chat.system_conversation import WeamDeepSeekCustomGPTSimpleChatService
from src.chatflow_langchain.repositories.custom_gpt_repository import CustomGPTRepository

custom_gpt_repo=CustomGPTRepository()

class WeamDeepSeekCustomGPTManager():
    def __init__(self):
        self.services = {
            "doc": WeamDeepSeekCustomGPTDocChatService(),
            "simple": WeamDeepSeekCustomGPTSimpleChatService(),
        }
        self.handler_map = {
            "doc": self.custom_gpt_doc_handler,
            "simple": self.custom_gpt_simple_handler,
        }
    def Initilization_custom_gpt(self,custom_gpt_id:str=None,customgptmodel:str=None):
        """
        Initializes the Custom GPT with the specified API key and company model.

        Parameters
        ----------
        custom_gpt_id : str, optional
            The API key ID used for decryption and initialization.
        customgptmodel : str, optional
            The company model configuration for the LLM.

        Exceptions
        ----------
        Logs an error if the initialization fails.
        """
        try:
        
            custom_gpt_repo.initialization(custom_gpt_id=custom_gpt_id, collection_name=customgptmodel)
            
        except Exception as e:
            logger.error(
                f"Failed to initialize custom gpt: {e}",
                extra={"tags": {"method": "CustomGPTStreamingDocChatService.Initilization_custom_gpt"}}
            )
            raise HTTPException(status_code=400, detail=f"Failed to initialize custom gpt: {e}")
        
    async def custom_gpt_doc_handler(self,chat_input,**kwargs): 
        customgpt_doc_chat=self.services['doc']
        query = chat_input.query
        customgpt_doc_chat.Initilization_custom_gpt(
            custom_gpt_id=chat_input.custom_gpt_id,
            customgptmodel=chat_input.customgptmodel
        )
        customgpt_doc_chat.initialize_llm(company_id=chat_input.company_id,companymodel=chat_input.companymodel,llm_apikey=chat_input.llm_apikey,regenerated_flag=chat_input.isregenerated)
        customgpt_doc_chat.initialize_repository(
            chat_session_id=chat_input.chat_session_id,
            collection_name=chat_input.threadmodel,
            thread_id=chat_input.thread_id,
            regenerated_flag=chat_input.isregenerated
        )
        
        customgpt_doc_chat.load_vector_store(
            companypinecone_collection=chat_input.companypinecone,
            company_model_collection=chat_input.companymodel,
            company_apikey_id=chat_input.company_id,
            chat_doc_collection=chat_input.chat_docs_collection,
            extra_files_ids=chat_input.extra_file_ids,
            extra_tags=chat_input.extra_tags,
            query=chat_input.query
        )
        customgpt_doc_chat.prompt_attach(additional_prompt_id=chat_input.prompt_id, collection_name=chat_input.promptmodel)
        customgpt_doc_chat.create_conversation(input_text=query,regenerated_flag=chat_input.isregenerated)
        response_generator = customgpt_doc_chat.stream_run_conversation(chat_input.thread_id, chat_input.threadmodel, isMedia=chat_input.isMedia,delay_chunk=chat_input.delay_chunk,regenerated_flag=chat_input.isregenerated,msgCredit=chat_input.msgCredit,is_paid_user=chat_input.is_paid_user)

        return response_generator

    async def custom_gpt_simple_handler(self,chat_input,**kwargs): 
        customgpt_simple_chat=self.services['simple']
        query = chat_input.query
        customgpt_simple_chat.Initilization_custom_gpt(
            custom_gpt_id=chat_input.custom_gpt_id,
            customgptmodel=chat_input.customgptmodel
        )
        customgpt_simple_chat.initialize_llm(company_id=chat_input.company_id,companymodel=chat_input.companymodel,llm_apikey=chat_input.llm_apikey,regenerated_flag=chat_input.isregenerated)
        customgpt_simple_chat.initialize_repository(
            chat_session_id=chat_input.chat_session_id,
            collection_name=chat_input.threadmodel,
            thread_id=chat_input.thread_id,
            regenerated_flag=chat_input.isregenerated
        )
        
        customgpt_simple_chat.prompt_attach(additional_prompt_id=chat_input.prompt_id, collection_name=chat_input.promptmodel)
        customgpt_simple_chat.create_conversation(input_text=query,image_url=chat_input.image_url,regenerated_flag=chat_input.isregenerated)
        response_generator = customgpt_simple_chat.stream_run_conversation(chat_input.thread_id, chat_input.threadmodel, isMedia=chat_input.isMedia,delay_chunk=chat_input.delay_chunk,regenerated_flag=chat_input.isregenerated,msgCredit=chat_input.msgCredit,is_paid_user=chat_input.is_paid_user)
        return response_generator
    

    
    async def custom_gpt_chat_handler(self, chat_input, **kwargs):
        # Determine the handler based on the prefix of custom_gpt_id
     
        if custom_gpt_repo.get_doc_flag() or chat_input.extra_file_ids:
            handler = self.handler_map.get('doc', self.custom_gpt_doc_handler)
        else:
            handler = self.handler_map.get('simple', self.custom_gpt_simple_handler)

        return await handler(chat_input, **kwargs)


        