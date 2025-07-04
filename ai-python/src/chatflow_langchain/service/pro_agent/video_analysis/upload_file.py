from google import genai
import time
import os
from fastapi.responses import JSONResponse
from src.chatflow_langchain.service.config.model_config_gemini import DefaultGEMINI20FlashModelRepository
from src.chatflow_langchain.repositories.file_repository import FileRepository
from src.chatflow_langchain.service.pro_agent.video_analysis.utils import extract_video_id, get_video_url,extract_main_domain
from src.chatflow_langchain.service.pro_agent.video_analysis.config import  VideoValidation
from src.celery_service.upload_file.video import upload_gemini_video
from src.crypto_hub.utils.crypto_utils import crypto_service
from src.gateway.exceptions import PayloadTooLargeException
from fastapi.encoders import jsonable_encoder
from src.db.config import get_field_by_name
from fastapi import HTTPException, status
from dotenv import load_dotenv
load_dotenv()

class UploadFileService:
    def __init__(self):
        """
        Initialize the LoomUploadFile class with the Gemini API key.
        """
        self.file_repository = FileRepository()
        self.upload_method_dict = {
            "loom": self.upload_loom_to_gemini,
        }

    def get_size(self, num_bytes):
        gb = num_bytes / (1024 ** 3)
        return gb

    async def initialize_chat_input(self,chat_input):
        self.chat_input = chat_input
        self.company_id=chat_input.company_id
        self.companymodel=chat_input.companymodel
        self.agent_extra_info=chat_input.agent_extra_info
        self.url=self.agent_extra_info.get("url","")
        self.cdn_url=self.agent_extra_info.get("cdn_url",None)
        self.delay_chunk=chat_input.delay_chunk
        self.file_collection=chat_input.file_collection
        self.domain=extract_main_domain(self.url)
        self.pro_agent_details = get_field_by_name('setting', 'PRO_AGENT', 'details')
        self.size = int(self.agent_extra_info.get("size", 0))

    async def upload_loom_to_gemini(self) -> dict:
        """
        Upload a file to Gemini storage and return the response metadata.
        """
        try:
           

            if self.cdn_url is None:
                self.video_id= extract_video_id(self.url)
                self.video_url = get_video_url(self.video_id) 
            
            else:
                self.video_url=self.cdn_url
            local_environment = os.getenv("WEAM_ENVIRONMENT", "local")
            if local_environment in ["prod"]:          
                self.encrypt_key = self.pro_agent_details.get("qa_specialist").get("gemini")
                self.decrypt_key = crypto_service.decrypt(self.encrypt_key)

            else:
                self.model = DefaultGEMINI20FlashModelRepository(company_id=self.company_id,companymodel=self.companymodel)
                self.encrypt_key=self.model.get_encrypt_key()
                self.decrypt_key=self.model.get_decrypt_key()
            client = genai.Client(api_key=self.decrypt_key)

            total_bytes = 0
            for file in client.files.list():
                if file.state.name == "ACTIVE":  # Only count active files
                    total_bytes += file.size_bytes

            if (self.get_size(self.size) + self.get_size(total_bytes)) > 20:
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail="Storage limit exceeded. Please delete some files to free up space."
                )
        
            file_dict = upload_gemini_video.delay(self.video_url,encrypt_api_key=self.encrypt_key).get()
            if file_dict['duration']>VideoValidation.VIDEO_LIMIT:
                    raise PayloadTooLargeException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Video too long. Maximum allowed duration is 30 minutes.")


            response=client.files.get(name=file_dict.get("gemini_file_name"))
            while response.state.name == 'PROCESSING':
                time.sleep(2)
                response = client.files.get(name=response.name) 
            
            google_file_metadata=response.dict()
            

            file_id=self.file_repository.insert_file(file_data={"google_metadata":google_file_metadata},collection_name=self.file_collection)
            

            return JSONResponse(
                content={
                "status": 200,
                "message": "Your request has been processed successfully.",
                "data": jsonable_encoder(google_file_metadata)
                },
                status_code=status.HTTP_200_OK)
        except HTTPException as he:
            raise he
        except Exception as e:
            raise RuntimeError(f"Failed to upload file to Gemini: {e}")

    async def upload_file(self) -> dict:
        """
        Upload a file to the specified storage method.
        """
        if self.domain in self.upload_method_dict:
            return await self.upload_method_dict[self.domain]()
        else:
            raise ValueError(f"Unsupported domain: {self.domain}")