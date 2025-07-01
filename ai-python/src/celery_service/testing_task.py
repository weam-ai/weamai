from src.celery_service.celery_worker import celery_app
@celery_app.task
def add(x,y):
    return "AI"+x+y