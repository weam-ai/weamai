import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Service.config import Dev
from Service.api_service import APIService
from locust import HttpUser, task, between
from shuffled_payload import shuffled_payloads

class LoadTestUser(HttpUser):
    wait_time = between(1, 5)

    host = Dev.HOST

    def on_start(self):
        self.api_service = APIService(
            client=self.client,
            host=Dev.HOST,
            origin=Dev.ORIGIN,
            jwt_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY2ZTEyNDRiYTYzNDRlNzUxZmFmNzMwYSIsImVtYWlsIjoibnNoaW5nYWRpeWFAdGFza21lLmJpeiIsImlhdCI6MTczMjUwODM3NiwiZXhwIjoxNzMyNTk0Nzc2fQ.sqdmXXopIk4m8DA_5lhdE5gvd4mZTM-L75tWephIOWU"  # Replace with your actual JWT token
        )

    # @task
    # def hello_world(self):
    #     self.api_service.get_ping()

    @task
    def post_api_test(self):
        url = Dev.TOOL_CHAT_URL  # Ensure this is defined in your config
        for payload in shuffled_payloads:
            self.api_service.post_title(url, payload)  # Send each shuffled payload
