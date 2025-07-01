
# Setting Up and Running Locust Tests

Follow these steps to set up your environment and run Locust tests for different configurations.

## Prerequisites
- Ensure Python 3.x is installed on your machine.
- Install `pip` if not already available.

---

## Steps to Setup and Run Locust

### 1. Create and Activate a Virtual Environment
```bash
python3 -m venv test_venv
source ./test_venv/bin/activate
```

### 2. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 3. Navigate to the Static-Payload Directory
```bash
cd Static-Payload
```

### 4. Run Locust with the Appropriate Configuration

#### Development Environment
```bash
locust -f dev_locustfile.py
```

#### Local Environment
```bash
locust -f local_locustfile.py
```

#### QA Environment
```bash
locust -f qa_locustfile.py
```
