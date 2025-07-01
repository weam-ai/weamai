import time
from locust_logger import logger
from .utils import PDFReport

class APIService:
    def __init__(self, client, host, origin, jwt_token):
        self.client = client
        self.host = host
        self.origin = origin
        self.jwt_token = jwt_token
        self.pdf_report = PDFReport()
        self.timeout = 120

    def get_ping(self):
        url = f"{self.host}/ping"
        start_time = time.perf_counter()

        with self.client.get(url, catch_response=True, timeout=self.timeout) as response:
            total_time = time.perf_counter() - start_time

            if response.status_code in (200, 207):
                logger.info(f"POST {url} successful in {total_time:.2f} seconds")
                self.pdf_report.add_response_time("GET", url, total_time, response.status_code)
                response.success()
            else:
                logger.error(f"GET {url} failed with status code {response.status_code}")
                self.pdf_report.add_response_time("GET", url, total_time, response.status_code)
                response.failure(f"Failed with status code {response.status_code}")

    def post_title(self, url, payload):
        headers = {
            "Authorization": f"jwt {self.jwt_token}",
            "origin": self.origin
        }

        start_time = time.perf_counter()
        with self.client.post(url, json=payload, headers=headers, catch_response=True, timeout=self.timeout) as response:
            total_time = time.perf_counter() - start_time
            self.pdf_report.add_response_time("POST", url, total_time, response.status_code)  # Log the response time
            if response.status_code == 200:
                logger.info(f"POST {url} successful in {total_time:.2f} seconds")
                response.success()
            else:
                logger.error(f"POST {url} failed with status code {response.status_code} in {total_time:.2f} seconds")
                response.failure(f"Failed with status code {response.status_code}")
    
    def generate_pdf_report(self):
        # Once all API calls are made, generate the PDF report
        self.pdf_report.create_pdf()