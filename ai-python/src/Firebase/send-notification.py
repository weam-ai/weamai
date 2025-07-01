from fastapi import FastAPI, HTTPException
from src.gateway.schema.firebase import NotificationRequest
from firebase import firebase

app = FastAPI()

@app.post("/send-notification/")
async def send_notification(request: NotificationRequest):
    try:
        response = firebase.send_push_notification(request.token, request.title, request.body)
        return {"message": "Notification sent successfully", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
