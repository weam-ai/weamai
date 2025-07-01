import asyncio
from langchain_openai import ChatOpenAI
from langchain.chains.llm import LLMChain
from fastapi.responses import JSONResponse
from src.logger.default_logger import logger
from src.chatflow_langchain.service.config.model_config_openai import OPENAIMODEL, DefaultGPT4oMiniModelRepository
from src.chatflow_langchain.service.pro_agent.seo_optimizer.chat_prompt_factory import create_prompt_topic
from langchain_community.callbacks.manager import get_openai_callback
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from fuzzywuzzy import fuzz, process
import hashlib
from src.db.config import db_instance
from fastapi import status
class TopicGenerator:
    def __init__(self, current_user_data):
        self.thread_repo = ThreadRepostiory()
        self.current_user_data = current_user_data
        self.llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()

    async def initialize_chat_input(self, chat_input):
        self.company_id = chat_input.company_id
        self.thread_id = chat_input.thread_id
        self.user_id = str(self.current_user_data["_id"])
        self.thread_model = chat_input.threadmodel
        self.companymodel = chat_input.companymodel
        self.selected_keywords_hold=chat_input.agent_extra_info.get("primary_keywords","")
        self.selected_keywords = "".join(self.selected_keywords_hold)
        self.secondary_keywords = chat_input.agent_extra_info.get("secondary_keywords", [])

        self.thread_repo.initialization_thread_id(self.thread_id, collection_name=self.thread_model)
        self.agent_extra_info = self.thread_repo.get_agent_extra_info()

        self.business_summary = self.agent_extra_info.get("business_summary", "No summary provided")
        self.target_keywords = self.agent_extra_info.get("target_keywords", [])
        self.website_url = self.agent_extra_info.get("website_url", "Not Specified")
        self.target_audience = self.agent_extra_info.get("target_audience", "Not Specified")

    async def initialize_llm(self):
        try:
     
            self.api_key_id = DefaultGPT4oMiniModelRepository(self.company_id, self.companymodel).get_default_model_key()
            self.llm_apikey_decrypt_service.initialization(self.api_key_id, self.companymodel)
            self.model_name = OPENAIMODEL.MODEL_VERSIONS[self.llm_apikey_decrypt_service.model_name]
            self.llm = ChatOpenAI(
                model_name=self.model_name,
                temperature=0.7,
                api_key=self.llm_apikey_decrypt_service.decrypt(),
                streaming=False,
                verbose=False,
                stream_usage=True
            )
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise

    async def create_prompt(self):
        self.topic_prompt = create_prompt_topic()

    async def create_chain(self):
        try:
            self.topic_chain = LLMChain(llm=self.llm, prompt=self.topic_prompt)
        except Exception as e:
            logger.error(f"Error creating LLM chain: {e}")

    async def run_chain(self):
        """Runs the LLM chain to generate topics and ensures uniqueness."""
        with get_openai_callback() as cb:
            try:
                logger.info("Running topic generation chain...")
                self.generated_topics = await self.topic_chain.ainvoke({
                    'website': self.website_url,
                    'business_summary': self.business_summary,
                    'target_audience': self.target_audience,
                    'selected_keywords': self.selected_keywords,
                })
                self.generated_topics = self.generated_topics['text']

                logger.info(f"Generated topics: {self.generated_topics}")

                # Validate topics and regenerate if necessary
                self.generated_topics = await self.validate_generated_topic(self.generated_topics)

                self.cb = cb
                await asyncio.to_thread(self.perform_thread_operations)

                logger.info("Topic generation completed successfully.")
                return JSONResponse(
                    content={
                        "status": status.HTTP_200_OK,
                        "message": "Topic generation successful.",
                        "data": {"topics": self.generated_topics}
                    },
                    status_code=status.HTTP_200_OK
                )
            except Exception as e:
                logger.error(f"Error running topic generation chain: {e}", exc_info=True)
                return JSONResponse(
                    content={"status": status.HTTP_400_BAD_REQUEST, "message": "Failed to generate topics"},
                    status_code=status.HTTP_400_BAD_REQUEST
                )

    async def validate_generated_topic(self, topic):
        """Checks if the generated topic is too similar to existing ones and regenerates only if necessary."""
        logger.info(f"Validating topic: {topic}")

        max_attempts = 3
        attempts = 0

        url_hash = hashlib.sha256(self.website_url.encode()).hexdigest()

        while attempts < max_attempts:
            try:
                similar_titles = self.find_similar_topic_by_website_hash(url_hash, topic)
            except Exception as e:
                logger.error(f"Error finding similar topics: {e}", exc_info=True)
                return topic

            # If no similar titles, return immediately
            if not similar_titles:
                logger.info(f"Topic '{topic}' is unique. Returning.")
                return topic

            logger.warning(f"Topic '{topic}' is too similar to existing ones. Regenerating...")
            attempts += 1

            try:
                regenerated_topic = await self.topic_chain.ainvoke({
                    'website': self.website_url,
                    'business_summary': self.business_summary,
                    'target_audience': self.target_audience,
                    'selected_keywords': self.selected_keywords,
                    'avoid_similar': topic
                })
                topic = regenerated_topic.get('text', '').strip()
                logger.info(f"Regenerated topic: {topic}")
            except Exception as e:
                logger.error(f"Error generating new topic: {e}", exc_info=True)
                return topic

            try:
                new_similar_titles = self.find_similar_topic_by_website_hash(url_hash, topic)
            except Exception as e:
                logger.error(f"Error checking newly generated topic: {e}", exc_info=True)
                return topic

            if not new_similar_titles:
                logger.info(f"New topic '{topic}' is unique. Returning.")
                return topic  # Exit early if the new topic is unique

        return topic  # If max attempts are reached, return the last generated topic


    def find_similar_topic_by_website_hash(self, url_hash, topic, limit=10, similarity_threshold=80):
        """Finds similar topics using fuzzy matching and ensures uniqueness."""
        try:
            sitemap_instance = db_instance.get_collection("sitemaps")
            record = sitemap_instance.find_one({"website_hash_id": url_hash}, {"blog_titles.title": 1})
            if not record:
                logger.warning("No record found with the given ID.")
                return []

            titles_list = record.get("blog_titles", {}).get("title", [])
            
            if not titles_list:
                logger.warning("No titles found in the record.")
                return []
            similar_titles = process.extract(topic, titles_list, scorer=fuzz.partial_ratio, limit=limit)
            filtered_titles = [title for title, score in similar_titles if score > similarity_threshold]
            return filtered_titles

        except Exception as e:
            logger.error(f"Error in searching similar titles: {e}", exc_info=True)
            return []

    def perform_thread_operations(self):
        self.topic_data = {
            "$set": {
                "proAgentData.step3":  {"topics": self.generated_topics,'primary_keywords': self.selected_keywords_hold,"secondary_keywords": self.secondary_keywords}, 
            }
        }
        self.thread_repo.update_fields(data=self.topic_data)
        self.thread_repo.update_token_usage(cb=self.cb)