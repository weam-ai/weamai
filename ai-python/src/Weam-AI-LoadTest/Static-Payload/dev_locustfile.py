import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Service.config import Dev, DevPayload, BaseConfig
from Service.api_service import APIService
from locust import HttpUser, task, between

class LoadTestUser(HttpUser):
    wait_time = between(1, 5)

    host = Dev.HOST
    # Define the base URL and other configuration for APIService
    def on_start(self):
        # Create the API service instance using the client, host, origin, and JWT token
        self.api_service = APIService(
            client=self.client,
            host=Dev.HOST,
            origin=Dev.ORIGIN,
            # jwt_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY2ZTI4OTJmYTA3NGQyZTVmYzZiYWI3ZCIsImVtYWlsIjoiZGhydXZpc2hwYXRlbEB0YXNrbWUuYml6IiwiaWF0IjoxNzMyMDgxNzYwLCJleHAiOjE3MzIxNjgxNjB9.wUUhGCdEWmrXeC0BoMq5TsqqKCrKAfFfQMPNuQNlmWE")
            jwt_token=BaseConfig.JWT_TOKEN)

    # @task
    # def hello_world(self):
    #     self.api_service.get_ping()

    @task
    def post_api_test(self):
        url = Dev.VECTOR_STORE_URL
        payload = DevPayload.VECTOR_STORE
        self.api_service.post_title(url, payload)

    def on_stop(self):
        # Generate the PDF report when the test stops
        self.api_service.generate_pdf_report()
