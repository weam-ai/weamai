from fastapi import File, UploadFile,Form
from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException, Depends, status
from bson import ObjectId
from src.gateway.schema.import_chat import ImportChatBase
from src.chatflow_langchain.controller.import_chat_hub import ImportChatController
from src.gateway.jwt_decode import get_user_data
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Annotated
from src.logger.default_logger import logger
from fastapi.responses import JSONResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/import_chat",
    summary="Import Chat",
    description="Endpoint to Import chat from openai and anthropic",
    response_description="Response message containing whether import successful or not",)
async def upload_file(request: Request,
    user_id: Annotated[str, Form(..., description="User ID")],
    company_id: Annotated[str, Form(..., description="Company ID")],
    brain_id:Annotated[str,Form(...,description="brain id")],
    brain_title:Annotated[str,Form(...,description="brain title.")],
    brain_slug:Annotated[str,Form(...,description="brain slug")],
    company_name:Annotated[str,Form(...,description="company name.")],
    companymodel:Annotated[str,Form(...,description="The name of the collection.")]='companymodel',
    file: UploadFile = File(...),
    current_user=Depends(get_user_data)):
    try:
        # Generate a unique import ID
        import_id = ObjectId()
        import_chat_service = ImportChatController()
        # Define the S3 upload folder and key
        file_content = await file.read()
        # Read the file content as bytes
        import_input = ImportChatBase(user_id=user_id, company_id=company_id,brain_id=brain_id,brain_slug=brain_slug,brain_title=brain_title,company_name=company_name,companymodel=companymodel)
        import_chat_service.initialize(import_id,import_input)
        await import_chat_service.upload_file(file,file_content)
        await import_chat_service.get_import_data(current_user=current_user)
        import_chat_service.pipeline_initlization()
        await import_chat_service.process_conversations()

        logger.info("File upload and processing completed successfully",
                extra={"import_id": str(import_id), "file_name": file.filename})
        return JSONResponse(content={"status_code": status.HTTP_200_OK,  # Root level status code
            "data": {
                "filename": file.filename,
                "message": "Your chats are being imported. Please wait, as this might take a moment. Only text will be included images won't be imported. We will notify you via email once the import is successfully completed. Thank you for your patience!",
                "status_code": status.HTTP_200_OK  # Status code inside data
            }
        },status_code=status.HTTP_200_OK)
    except HTTPException as he:
        logger.error(
            "HTTP error executing Chat With Import Chat API",
            extra={
                "tags": {
                    "endpoint": "/import_chat",
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI

    except Exception as e:
        logger.error(
            f"Error executing task: {e}",
            extra={"tags": {"endpoint": "/import_chat"}}
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
