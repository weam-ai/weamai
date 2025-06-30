from pydantic import BaseModel

class NotificationRequest(BaseModel):
    token: str
    title: str
    body: str
