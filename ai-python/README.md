# Go Custom AI: Empowering Businesses with Advanced GPT Solutions

## Product Vision
Go Custom AI aims to empower companies with advanced, customizable GPT solutions tailored to their specific needs. Our vision is to foster collaboration and knowledge sharing among teams through an intuitive workspace environment.

## Target Users
Our platform caters to businesses in search of AI-powered chatbots for specialized use cases and marketing agencies looking to offer bespoke GPT solutions to their clients.

## Introducing Go Custom AI

### Revolutionizing AI Solutions
Go Custom AI is a groundbreaking multi-user SaaS platform designed to revolutionize how businesses harness the power of Large Language Models (LLMs). With our platform, users can seamlessly integrate API keys from their preferred LLM providers, such as OpenAI and Anthropic, to access a diverse range of robust model


## Table of Contents

- [Go Custom AI: Empowering Businesses with Advanced GPT Solutions](#go-custom-ai-empowering-businesses-with-advanced-gpt-solutions)
  - [Product Vision](#product-vision)
  - [Target Users](#target-users)
  - [Introducing Go Custom AI](#introducing-go-custom-ai)
    - [Revolutionizing AI Solutions](#revolutionizing-ai-solutions)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Running Services](#running-services)
  - [Monitoring and Logging](#monitoring-and-logging)
    - [Serving with Ray](#serving-with-ray)
  - [Additional Documentation](#additional-documentation)
  - [Environment Variables](#environment-variables)
  - [Enterprise-Level Layer Project Architecture](#enterprise-level-layer-project-architecture)
    - [Service Layer:](#service-layer)
    - [Models:](#models)
    - [Repositories:](#repositories)
    - [Test Cases:](#test-cases)
    - [Utils:](#utils)

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/rutvi1920/gocustomai
    cd /gocustomai/backend_python/service
    ```

2. **Set up environment variables:**

    Create a `.env_local` file based on the provided `.env_example` file and fill in the necessary environment variables.

3. **Install dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Build Docker images:**

- **Development:**

    ```sh
    docker-compose --env-file=.env_dev up --build
    ```

- **QA:**

    ```sh
    docker-compose --env-file=.env_qa up --build
    ```

- **Production:**

    ```sh
    docker-compose --env-file=.env_prod up --build 
    ```


## Usage

### Running Services

You can run different sets of services using the provided Docker Compose files:

- **To run the default set of services:**

    ```sh
    docker-compose --env-file=.env_local up
    ```

- **To run the services with logging and monitoring:**

    ```sh
    docker-compose -f docker-compose-logger.yml up
    ```

## Monitoring and Logging

- **Prometheus:** Access Prometheus at `http://localhost:<PROMETHEUS_PORT_OUT>`.
- **Grafana:** Access Grafana at `http://localhost:<GRAFANA_PORT_OUT>` using the credentials set in the environment variables.
- **Loki and Promtail:** Logging is configured via Promtail to ship logs to Loki, which can be visualized in Grafana.

### Serving with Ray

Ray Serve allows you to serve your FastAPI application with high scalability. Use the `docker-compose-serve.yml` to start Ray Serve services. Use Ray Serve for custom LLM and custom embedding deployment.

**Note:** If you have a GPU in your system, use this file to leverage GPU capabilities.

```sh
docker-compose -f docker-compose-serve.yml --env-file=./ray_serve_app/.env_local.env up --build
```

## Additional Documentation

For detailed information about specific services, refer to the following documents:

- **Embedding Service:** [embedding_service.md](documents/embedding_service.md)
- **Extraction Service:** [extraction_service.md](documents/extraction_service.md)
- **Ray Service:** [ray_service.md](documents/ray_service.md)

## Environment Variables

The project uses a .env_local file to manage environment variables. Make sure to create this file and set the required variables as per your setup.

## Enterprise-Level Layer Project Architecture

### Service Layer:
- **Purpose:** The service layer encapsulates the application's business logic, orchestrates interactions between different components, and ensures the enforcement of business rules. It serves as a bridge between the presentation layer and the data layer.
- **Responsibilities:**
  - Implements business logic and rules.
  - Coordinates interactions between different components of the application.
  - Provides a high-level interface for executing complex operations.
- **Implementation:**
  - Contains methods or functions that represent specific business operations.
  - Utilizes repositories for data access but focuses on orchestrating operations rather than direct data manipulation.
- **Relationships:**
  - **Dependency:** Services rely on repositories for data access. The service layer utilizes repository methods to perform CRUD (Create, Read, Update, Delete) operations as part of its business logic.
  - **Abstraction:** The repository pattern abstracts data access details, while the service layer abstracts business logic implementation. Together, they ensure a separation of concerns, enhancing modularity and maintainability.

### Models:
- **Purpose:** Models represent the structure and behavior of data within the application. They encapsulate the application's data, along with its validation rules and relationships.
- **Responsibilities:**
  - Define the structure of data entities.
  - Implement data validation rules.
  - Establish relationships between different data entities.
- **Implementation:**
  - Typically implemented as classes or data structures.
  - May include methods for data manipulation and validation.

### Repositories:
- **Purpose:** Repositories provide an abstraction layer for data access. They encapsulate the logic for retrieving, storing, updating, and deleting data from the underlying data storage.
- **Responsibilities:**
  - Handle data access operations.
  - Abstract away the details of data storage mechanisms.
  - Provide a consistent interface for interacting with the data layer.
- **Implementation:**
  - Contains methods for CRUD operations on data entities.
  - Utilizes data access mechanisms such as database queries or API calls.
  - May include caching mechanisms for optimizing data access performance.

### Test Cases:
- **Purpose:** Test cases ensure the correctness and robustness of the application by validating its functionality under different scenarios.
- **Responsibilities:**
  - Verify that each component of the application behaves as expected.
  - Identify and address any defects or inconsistencies in the application's behavior.
- **Implementation:**
  - Written as automated tests using testing frameworks such as JUnit, pytest, or Jasmine.
  - Cover various use cases and edge cases to ensure comprehensive test coverage.
  - Include both unit tests for individual components and integration tests for testing interactions between components.
- **Running Test Cases:**
  - Use the following command to run test cases using Docker Compose:
  
    ```sh
    `docker-compose --env-file .env_qa -f docker-compose-test.yml up --build`
    ```

- **Running Prometheus Metrices:**
  - Use the following command to run prometheus using Docker Compose:
  
    ```sh
    `docker-compose --env-file .env_local -f docker-compose-prometheus.yml up --build`
    ```

### Utils:
- **Purpose:** Utils, short for utilities, provide reusable functions or utilities that are commonly used across the application.
- **Responsibilities:**
  - Implement common functionality that doesn't belong to a specific component.
  - Encapsulate reusable code to promote code reuse and maintainability.
- **Implementation:**
  - Consist of functions or classes that provide specific utility functionality.
  - May include helper functions for string manipulation, date formatting., error handling, etc.
  - Organized into modules or packages for easy access and maintenance.

