from fastapi import HTTPException, APIRouter, Request
from pydantic import BaseModel
from bson import ObjectId
from src.db.config import db_instance
from src.logger.default_logger import logger
from src.gateway.routers.migration.Delete_Record.utils import delete_failed_records
from src.gateway.utils import generate_csv_delete_report

importchat_collection = db_instance.get_collection("importChat")
company_collection = db_instance.get_collection("company")
replythread_collection = db_instance.get_collection("replythread")
brain_collection = db_instance.get_collection("brain")

router = APIRouter()
class DeleteRequest(BaseModel):
    import_id: str

@router.post("/delete_single_import_chat_records", summary="Delete Record for Import Chat")
async def delete_records(request: DeleteRequest):
    try:
        # Check if import ID exists quickly
        if importchat_collection.count_documents({"_id": ObjectId(request.import_id)}) == 0:
            return {"message": "No record found for the provided import ID"}

        # Fetch conversation data
        import_chat_data = importchat_collection.find_one(
            {"_id": ObjectId(request.import_id)}, {"conversationData": 1}
        )

        # Extract chat IDs safely
        chat_ids = list(import_chat_data.get("conversationData", {}).keys()) if import_chat_data else []

        # Delete dependent records
        deleted_records = await delete_failed_records(request.import_id, chat_ids)

        return {
            "message": "Deletion process completed successfully",
            "deleted_records": deleted_records
        }

    except Exception as e:
        logger.error(f"Error deleting records: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting records")

# class DeleteListRequest(BaseModel):
#     import_id: str
#     chat_ids: List[str]

# @router.post("/delete_provided_list_chat_ids_import_chat_dependent_records", summary="Delete Record for Import Chat")
# async def delete_records(request: DeleteListRequest):
#     try:
#         if importchat_collection.count_documents({"_id": ObjectId(request.import_id)}) == 0:
#             return {"message": "No record found for the provided import ID"}
#         deleted_records = await delete_failed_records(request.import_id, request.chat_ids)
#         return {"message": "Deletion process completed successfully", "deleted_records": deleted_records}
#     except Exception as e:
#         logger.error(f"Error deleting records: {str(e)}")
#         raise HTTPException(status_code=500, detail="Error deleting records")

class DeleteListRequest(BaseModel):
    import_ids: list

@router.post("/delete_all_import_chat_id_list_dependent_records", summary="Delete Records for Multiple Import Chats")
async def delete_records(request: DeleteListRequest):
    try:
        # document_ids = [str(doc["_id"]) for doc in importchat_collection.find({}, {"_id": 1})]
        # print("document_ids:",document_ids)
        import_ids = [ObjectId(import_id) for import_id in request.import_ids]  # Convert all import IDs to ObjectId

        import_chat_data = importchat_collection.find(
            {"_id": {"$in": import_ids}}, {"conversationData": 1}
        )
        
        # Extract chat IDs for each import ID
        chat_id_map = {
            str(data["_id"]): list(data.get("conversationData", {}).keys()) for data in import_chat_data
        }
        
        if not chat_id_map:
            return {"message": "No records found for the provided import IDs"}
        
        # Delete dependent records for all import IDs
        deleted_records = {}
        for import_id, chat_ids in chat_id_map.items():
            deleted_records[import_id] = await delete_failed_records(import_id, chat_ids)
        
        return {
            "message": "Deletion process completed successfully",
            "deleted_records": deleted_records
        }
    
    except Exception as e:
        logger.error(f"Error deleting records: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting records")

# List of collections to delete records from Brain ID's
collections_to_delete_brainIDS = ["chatdocs","notificationList","shareChat"]
collections_to_delete__id = ["brain"]
collections_to_delete_brain_id = ["chat","chatmember","customgpt","messages","prompts","sharebrain"]

# List of collections to delete records from Company ID's
collections_to_delete_companyIDS = ["bookmarks","sharebrainteam","teamUser","workspaceuser"]
collections_to_delete__id = ["company"]
collections_to_delete_company_id = ["companymodel","companypinecone","invoice","storagerequest","subscription","user","workspace"]

class ExcludeCompanyListRequest(BaseModel):
    exclude_company_ids: list

@router.post("/delete_all_exclude_company_id_dependent_records", summary="Delete Records for Multiple Company Ids")
async def delete_records(request: Request,data: ExcludeCompanyListRequest):
    try:

        # Fetch company documents based on include_ids
        company_documents = list(company_collection.find(
            {"_id": {"$nin": [ObjectId(id) for id in data.exclude_company_ids]}},
            {"_id": 1, "companyNm": 1, "users.id": 1}  # Fetch company ID, name, and user IDs
        ))

        # If no companies are found, return early
        if not company_documents:
            return {"message": "No companies found for deletion."}

        company_ids = []
        user_ids = []

        # Collect company IDs and user IDs
        for doc in company_documents:
            company_ids.append(doc["_id"])  # Collect company IDs
            if "users" in doc:
                user_ids.extend([user["id"] for user in doc["users"] if "id" in user])

        user_ids_obj = [ObjectId(user_id) for user_id in user_ids]

        # Prepare the response list
        deleted_companies = []

        # Perform deletions and calculate counts for each company
        for doc in company_documents:
            company_id = doc["_id"]
            company_name = doc.get("companyNm", "Unknown")

            # Fetch related brain IDs based on this specific company ID
            brain_ids = [
                doc["_id"] for doc in brain_collection.find(
                    {"companyId": company_id},
                    {"_id": 1}
                )
            ]

            # Convert to ObjectId type
            brain_ids_obj = [ObjectId(brain_id) for brain_id in brain_ids]
            company_ids_obj = [ObjectId(company_id)]

            # Initialize counters for this company
            deleted_brain_records = {}
            deleted_company_records = {}
            deleted_user_records = {}

            # Perform deletions for brain records related to this company
            for collection_name in collections_to_delete_brainIDS + collections_to_delete_brain_id:
                collection = db_instance.get_collection(collection_name)
                result = collection.delete_many({"$or": [
                    {"brainId": {"$in": brain_ids_obj}},
                    {"brain.id": {"$in": brain_ids_obj}}
                ]})
                deleted_brain_records[collection_name] = result.deleted_count
                logger.info(f"Deleted from {collection_name}: {result.deleted_count} records")

            # Delete from brain collection
            delete_brain_result = brain_collection.delete_many({"_id": {"$in": brain_ids_obj}})
            deleted_brain_records["brain_collection"] = delete_brain_result.deleted_count
            logger.info(f"Deleted from brain_collection: {delete_brain_result.deleted_count} records")

            # Perform deletions for company records related to this company
            for collection_name in collections_to_delete_companyIDS + collections_to_delete_company_id:
                collection = db_instance.get_collection(collection_name)
                result = collection.delete_many({"$or": [
                    {"companyId": {"$in": company_ids_obj}},
                    {"company.id": {"$in": company_ids_obj}}
                ]})
                deleted_company_records[collection_name] = result.deleted_count
                logger.info(f"Deleted from {collection_name}: {result.deleted_count} records")

            # Delete from company collection
            delete_company_result = company_collection.delete_many({"_id": {"$in": company_ids_obj}})
            deleted_company_records["company_collection"] = delete_company_result.deleted_count
            logger.info(f"Deleted from company_collection: {delete_company_result.deleted_count} records")

            # Perform deletions for user records from the replythread collection
            delete_replythread_result = replythread_collection.delete_many({"sender": {"$in": user_ids_obj}})
            deleted_user_records["replythread"] = delete_replythread_result.deleted_count
            logger.info(f"Deleted from replythread_collection: {delete_replythread_result.deleted_count} records")

            # Calculate total deleted records for this company
            total_deleted = (
                sum(deleted_brain_records.values()) +
                sum(deleted_company_records.values()) +
                deleted_user_records["replythread"]
            )

            # Append the company's data to the response
            deleted_companies.append({
                "company_id": str(company_id),
                "company_name": company_name,
                "total_deleted_records": total_deleted,
                "deleted_brain_records": deleted_brain_records,
                "deleted_company_records": deleted_company_records,
                "deleted_user_records": deleted_user_records
            })

        # Generate the CSV report for all deleted companies
        csv_report = generate_csv_delete_report(deleted_companies, request)

        return {
            "deleted_companies": deleted_companies,
            "csv_report": csv_report,
        }

    except Exception as e:
        logger.error(f"Error deleting records: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting records")
class IncludeCompanyListRequest(BaseModel):
    include_company_ids: list

@router.post("/delete_all_include_company_id_dependent_records", summary="Delete Records for Multiple Company Ids")
async def delete_records(request: Request,data: IncludeCompanyListRequest):
    try:
        company_ids_obj = [ObjectId(cid) for cid in data.include_company_ids]

        # Fetch company documents based on include_ids
        company_documents = list(company_collection.find(
            {"_id": {"$in": company_ids_obj}},
            {"_id": 1, "companyNm": 1, "users.id": 1} # Fetch company ID, name, and user IDs
        ))

        # If no companies are found, return early
        if not company_documents:
            return {"message": "No companies found for deletion."}

        company_ids = []
        user_ids = []

        # Collect company IDs and user IDs
        for doc in company_documents:
            company_ids.append(doc["_id"])  # Collect company IDs
            if "users" in doc:
                user_ids.extend([user["id"] for user in doc["users"] if "id" in user])

        user_ids_obj = [ObjectId(user_id) for user_id in user_ids]

        # Prepare the response list
        deleted_companies = []

        # Perform deletions and calculate counts for each company
        for doc in company_documents:
            company_id = doc["_id"]
            company_name = doc.get("companyNm", "Unknown")

            # Fetch related brain IDs based on this specific company ID
            brain_ids = [
                doc["_id"] for doc in brain_collection.find(
                    {"companyId": company_id},
                    {"_id": 1}
                )
            ]

            # Convert to ObjectId type
            brain_ids_obj = [ObjectId(brain_id) for brain_id in brain_ids]
            company_ids_obj = [ObjectId(company_id)]

            # Initialize counters for this company
            deleted_brain_records = {}
            deleted_company_records = {}
            deleted_user_records = {}

            # Perform deletions for brain records related to this company
            for collection_name in collections_to_delete_brainIDS + collections_to_delete_brain_id:
                collection = db_instance.get_collection(collection_name)
                result = collection.delete_many({"$or": [
                    {"brainId": {"$in": brain_ids_obj}},
                    {"brain.id": {"$in": brain_ids_obj}}
                ]})
                deleted_brain_records[collection_name] = result.deleted_count
                logger.info(f"Deleted from {collection_name}: {result.deleted_count} records")

            # Delete from brain collection
            delete_brain_result = brain_collection.delete_many({"_id": {"$in": brain_ids_obj}})
            deleted_brain_records["brain_collection"] = delete_brain_result.deleted_count
            logger.info(f"Deleted from brain_collection: {delete_brain_result.deleted_count} records")

            # Perform deletions for company records related to this company
            for collection_name in collections_to_delete_companyIDS + collections_to_delete_company_id:
                collection = db_instance.get_collection(collection_name)
                result = collection.delete_many({"$or": [
                    {"companyId": {"$in": company_ids_obj}},
                    {"company.id": {"$in": company_ids_obj}}
                ]})
                deleted_company_records[collection_name] = result.deleted_count
                logger.info(f"Deleted from {collection_name}: {result.deleted_count} records")

            # Delete from company collection
            delete_company_result = company_collection.delete_many({"_id": {"$in": company_ids_obj}})
            deleted_company_records["company_collection"] = delete_company_result.deleted_count
            logger.info(f"Deleted from company_collection: {delete_company_result.deleted_count} records")

            # Perform deletions for user records from the replythread collection
            delete_replythread_result = replythread_collection.delete_many({"sender": {"$in": user_ids_obj}})
            deleted_user_records["replythread"] = delete_replythread_result.deleted_count
            logger.info(f"Deleted from replythread_collection: {delete_replythread_result.deleted_count} records")

            # Calculate total deleted records for this company
            total_deleted = (
                sum(deleted_brain_records.values()) +
                sum(deleted_company_records.values()) +
                deleted_user_records["replythread"]
            )

            # Append the company's data to the response
            deleted_companies.append({
                "company_id": str(company_id),
                "company_name": company_name,
                "total_deleted_records": total_deleted,
                "deleted_brain_records": deleted_brain_records,
                "deleted_company_records": deleted_company_records,
                "deleted_user_records": deleted_user_records
            })

        # Generate the CSV report for all deleted companies
        csv_report = generate_csv_delete_report(deleted_companies, request)

        return {
            "deleted_companies": deleted_companies,
            "csv_report": csv_report,
        }

    except Exception as e:
        logger.error(f"Error deleting records: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting records")