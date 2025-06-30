from fastapi import APIRouter
from src.gateway.routers.migration.setting_migration import router as  migrate_setting
from src.gateway.routers.migration.companymodel_migration import router as migrate_company_models
from src.gateway.routers.migration.company_migration import router as migrate_company
from src.gateway.routers.migration.model_migration import router as migrate_model
from src.gateway.routers.migration.Delete_Record.delete_record import router as delete_import_chat_dependent
from src.gateway.routers.migration.dynamic_migration import router as dynamic_migration

migration_router = APIRouter()

migration_router.include_router(migrate_company_models, prefix="/companymodel", tags=["Company Model Migration"])
migration_router.include_router(migrate_company, prefix="/company", tags=["Company Migration"])
migration_router.include_router(migrate_model, prefix="/model", tags=["Model Migration"])
migration_router.include_router(migrate_setting, prefix="/setting", tags=["Setting Migration"])
migration_router.include_router(delete_import_chat_dependent, prefix="/delete", tags=["Delete Records"])
migration_router.include_router(dynamic_migration, prefix="/dynamic", tags=["Dynamic Migration"])
