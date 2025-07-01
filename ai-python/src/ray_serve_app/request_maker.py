import concurrent.futures
import requests
import random
import string
import time

def make_request(url, data):
    """Function to send a POST request to the specified URL with provided data."""
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    # Include the response content in the return values if needed for debugging or logging
    return response.status_code, url, response.json()

def random_string(length=100):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def process_batch(batch):
    """Process a batch of URLs with POST requests."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
        results = executor.map(lambda p: make_request(*p), batch)
        # for status_code, url, content in results:
        #     print(f"URL: {url}, Status Code: {status_code}, Response: {len(content['data'])}")

def main():
    urls = ["http://0.0.0.0:8073/model" for _ in range(1200)]
    data_payloads = [{'input': random_string()} for _ in urls]
    
    # Grouping URLs and data into batches of 100
    batch_size = 400
    batches = [(urls[i:i+batch_size], data_payloads[i:i+batch_size]) for i in range(0, len(urls), batch_size)]

    start_time = time.time()

    # Processing each batch
    for url_batch, data_batch in batches:
        batch = ((url, data) for url, data in zip(url_batch, data_batch))
        process_batch(batch)

    end_time = time.time()
    duration = end_time - start_time
    print(f"Completed in {duration:.2f} seconds")

if __name__ == "__main__":
    main()
