from src.chatflow_langchain.service.pro_agent.seo_optimizer.seo_client import RestClient
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
import os
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from src.logger.default_logger import logger
from src.chatflow_langchain.service.pro_agent.seo_optimizer.utils import sort_keywords_by_competition,refined_keyword_data
load_dotenv()
from src.db.config import get_field_by_name, get_decrypted_details

import asyncio
class KeywordResearchService:
    def __init__(self):
        """Initialize the service with API credentials and default location/language."""
        # settings_pro_agent_data = get_decrypted_details('setting', 'SEO_AGENT', 'details')
        SEO_USER_ID=os.environ.get("SEO_USER_ID")
        SEO_PASSWORD=os.environ.get("SEO_PASSWORD")

        if not SEO_USER_ID or not SEO_PASSWORD:
            raise ValueError("Missing SEO credentials: 'seoUserId' or 'SeoPassword' not found in the settings collection.")

        self.client = RestClient(SEO_USER_ID, SEO_PASSWORD)
        self.thread_repo = ThreadRepostiory()


    async def initialize_chat_input(self,chat_input):
        self.chat_input = chat_input
        self.company_id=chat_input.company_id
        self.thread_id=chat_input.thread_id
        self.thread_model=chat_input.threadmodel
        self.companymodel=chat_input.companymodel
        self.brain_id=chat_input.brain_id
        self.regenerated_flag=chat_input.isregenerated
        self.chat_session_id=chat_input.chat_session_id
        self.isregenerated=chat_input.isregenerated
        self.msgCredit=chat_input.msgCredit
        self.is_paid_user=chat_input.is_paid_user
        self.agent_extra_info=chat_input.agent_extra_info
        self.project_name=self.agent_extra_info.get("project_name","Unnamed Project")
        self.website_url=self.agent_extra_info.get("website_url","Not Specified")
        self.location=self.agent_extra_info.get("location","Not Specified")
        self.target_keywords=self.agent_extra_info.get("target_keywords","Not Specified")
        self.industry=self.agent_extra_info.get("industry"," ")
        self.business_summary=self.agent_extra_info.get("business_summary"," ")
        self.target_audience=self.agent_extra_info.get("target_audience"," ")
        self.language=self.agent_extra_info.get("language",[])
    
    async def get_recommended_keywords(self, limit=20):
        """Fetch recommended keywords based on base keywords."""

        post_data = {
            0: {
                "keywords": self.target_keywords,
                "location_name": self.location,
                "language_name": self.language,
                "limit": limit
            }
        }
        response = self.client.post("/v3/keywords_data/google_ads/keywords_for_keywords/live", post_data)
        
        if response["status_code"] == 20000:
            recommended_keywords = []
            tasks = response.get("tasks", [])
            if not tasks:
                return recommended_keywords  # Return empty list if no tasks

            for task in tasks:
                results = task.get("result", [])
                if results:
                    for result in results:
                        recommended_keywords.append(result.get("keyword", ""))  # Get keyword safely
            cost = task.get("cost", 0.0)  # Assuming cost is provided in the task level
            logger.info(f"API call cost: ${cost}")  # Log SERP API cost
            return list(set(filter(None, recommended_keywords)))[:limit]  # Remove None values
        else:
            raise Exception(f"Error fetching recommended keywords: {response['status_message']}")
    
    async def get_keyword_details(self, keywords):
        """Fetch search volume and additional details for a list of keywords."""
        if not keywords:
            return []  # Return empty list if no keywords

        post_data = {
            0: {
                "keywords": keywords,
                "location_name": self.location,
                "language_name": self.language
            }
        }
        response = self.client.post("/v3/keywords_data/google_ads/search_volume/live", post_data)
        
        if response["status_code"] == 20000:
            tasks = response.get("tasks", [])
            if not tasks:
                return []  # Return empty list if no tasks

            return tasks[0].get("result", []) or []  # Ensure it returns a list
        else:
            raise Exception(f"Error fetching search volume: {response['status_message']}")
    
    async def fetch_and_display_keywords(self, limit=20):
        """Fetch recommended keywords, merge them with base keywords, and display details."""
        try:
            # Fetch recommended keywords
            recommended_keywords = await self.get_recommended_keywords(limit)

            # Fetch details for base keywords
            base_keyword_details = await self.get_keyword_details(list(set(self.target_keywords)))
            self.base_filtered_data = refined_keyword_data(base_keyword_details, "left")
            # self.base_filtered_data = [
            #     {     
            #         "id": f"left-{index}",
            #         "keyword": item["keyword"],
            #         "search_volume": item["search_volume"] if item["search_volume"] else 0,
            #         "competition": item["competition"].capitalize() if item["competition"] else "LOW"
            #     }
            #     for index,item in enumerate(base_keyword_details)
            # ]

            # Fetch details for recommended keywords

            # self.base_filtered_data=[
            #             {    "id":"left-0",
            #                 "keyword": "Recall",
            #                 "search_volume": 74000,
            #                 "competition": "Low"
            #             },
            #             {   "id":"left-1",
            #                 "keyword": "Random Forest Tree",
            #                 "search_volume": 140,
            #                 "competition": "Low"
            #             },
            #             {   "id":"left-2",
            #                 "keyword": "Decision Tree",
            #                 "search_volume": 22200,
            #                 "competition": "Low"
            #             },
            #             {   "id":"left-3",
            #                 "keyword": "Machine Learning",
            #                 "search_volume": 49500,
            #                 "competition": "Low"
            #             },
            #             {   "id":"left-4",
            #                 "keyword": "Machine Learning AI",
            #                 "search_volume": 48500,
            #                 "competition": "Low"
            #             }
            #         ]
            recommended_keyword_details = await self.get_keyword_details(list(set(recommended_keywords)))
            self.recommended_filtered_data = refined_keyword_data(recommended_keyword_details, "right")
            # self.recommended_filtered_data = [
            #     {
            #         "id": f"right-{index}",
            #         "keyword": item["keyword"],
            #         "search_volume": item["search_volume"] if item["search_volume"] else 0,
            #         "competition": item["competition"].capitalize() if item["competition"] else "LOW"
            #     }
            #     for index,item in enumerate(recommended_keyword_details)
            # ]

            # self.recommended_filtered_data= [
            #             {  
            #                 "id":"right-0",
            #                 "keyword": "decision tree for clustering",
            #                 "search_volume": 10,
            #                 "competition": "Low"
            #             },
            #             {   "id":"right-1",
            #                 "keyword": "c4 5 decision tree example",
            #                 "search_volume": 10,
            #                 "competition": "Low"
            #             },
            #             {   "id":"right-2",
            #                 "keyword": "banana boat sunscreen recall",
            #                 "search_volume": 210,
            #                 "competition": "Low"
            #             },
            #             {   "id":"right-3",
            #                 "keyword": "design tree in machine learning",
            #                 "search_volume": 10,
            #                 "competition": None
            #             },
            #             {   "id":"right-4",
            #                 "keyword": "flutter machine learning",
            #                 "search_volume": 10,
            #                 "competition": "Low"
            #             }
            #         ]

            await asyncio.to_thread(self.perform_thread_operations)
            # Return response
            
            sorted_base_filtered_data = sort_keywords_by_competition(self.base_filtered_data)
            sorted_recommended_filtered_data = sort_keywords_by_competition(self.recommended_filtered_data)

            return JSONResponse(
                content={
                    "status": 200,
                    "message": "Your request has been processed successfully.",
                    "data": {
                            "targeted_keywords": sorted_base_filtered_data if sorted_base_filtered_data else [],
                            "recommended_keywords": sorted_recommended_filtered_data if sorted_recommended_filtered_data else []
                    }
                   
                },
                status_code=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error("An error occurred during keyword processing.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An unexpected error occurred while fetching and displaying keywords: {str(e)}")
        
    def perform_thread_operations(self):
        self.summary_data={"$set":{"proAgentData.step1":{"business_summary":self.business_summary,"target_audience":self.target_audience, \
                                                            "target_keywords":self.target_keywords,"website":self.website_url, \
                                                            "language":self.language,"location":self.location},"proAgentData.step2":{"targeted_volumes":self.base_filtered_data,"recommended_volumes":self.recommended_filtered_data}}}
        self.thread_repo.initialization(self.thread_id, collection_name=self.thread_model)
        self.thread_repo.update_fields(data=self.summary_data)
        if self.is_paid_user:
            self.thread_repo.update_credits(msgCredit=self.msgCredit)
        

