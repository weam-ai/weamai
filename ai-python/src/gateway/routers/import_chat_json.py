from fastapi import File, UploadFile,Form
from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException, Depends, status
from bson import ObjectId
from src.gateway.schema.import_chat import ImportChatJsonBase
from src.chatflow_langchain.controller.import_chat_json_controller import ImportChatController
from src.gateway.jwt_decode import get_user_data
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Annotated
from src.logger.default_logger import logger
from fastapi.responses import JSONResponse
from src.gateway.utils import validate_source_and_file, format_user_data

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/import_chat_json",
    summary="Import Chat Json",
    description="Endpoint to Import chat Json from openai and anthropic",
    response_description="Response message containing whether import successful or not",)
async def upload_file(request: Request,
    user_id: Annotated[str, Form(..., description="User ID")],
    company_id: Annotated[str, Form(..., description="Company ID")],
    brain_id:Annotated[str,Form(...,description="brain id")],
    brain_title:Annotated[str,Form(...,description="brain title.")],
    brain_slug:Annotated[str,Form(...,description="brain slug")],
    company_name:Annotated[str,Form(...,description="company name.")],
    companymodel:Annotated[str,Form(...,description="The name of the collection.")]='companymodel',
    code:Annotated[str,Form(...,description="Code Name.")]='OPENAI',
    file: UploadFile = File(...),
    current_user=Depends(get_user_data)):
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Invalid file type. Only JSON files are allowed.")

        # Read file content
        file_content = await file.read()

        user_data = format_user_data(current_user)
        validate_source_and_file(file_content, code, user_data, brain_title)
    
        import_id = ObjectId()
        import_chat_service = ImportChatController()
        import_input = ImportChatJsonBase(
            user_id=user_id, company_id=company_id, brain_id=brain_id,
            brain_slug=brain_slug, brain_title=brain_title,
            company_name=company_name, companymodel=companymodel,code=code
        )

        # Initialize and process the import
        import_chat_service.initialize(import_id, import_input)
        await import_chat_service.upload_file(file, file_content)
        await import_chat_service.get_import_data(current_user=current_user)
        import_chat_service.pipeline_initlization(code=code)
        await import_chat_service.process_conversations()

        logger.info("File upload and processing completed successfully",
                extra={"import_id": str(import_id), "file_name": file.filename})
        return JSONResponse(content={"status_code": status.HTTP_200_OK,  # Root level status code
            "data": {
                "filename": file.filename,
                "message": "Your chats are being imported. Please wait, as this might take a moment. Only text will be included images won't be imported. We will notify you via email once the import is successfully completed. Thank you for your patience!",
                "import_id": str(import_id),
                "status_code": status.HTTP_200_OK  # Status code inside data
            }
        },status_code=status.HTTP_200_OK)
    except HTTPException as he:
        logger.error(
            "HTTP error executing Chat With Import Chat Json API",
            extra={
                "tags": {
                    "endpoint": "/import_chat_json",
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI

    except Exception as e:
        logger.error(
            f"Error executing task: {e}",
            extra={"tags": {"endpoint": "/import_chat_json"}}
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
