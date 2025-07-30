
***

# Transcript Analysis API

This project is a web API built with Python and FastAPI that analyzes plain text transcripts to generate a concise summary and a list of actionable next steps. It is designed using a **Hexagonal (Ports and Adapters) Architecture** to ensure a clean separation of concerns, making the application highly modular, scalable, and testable.

## Architectural Design

The application follows the principles of Hexagonal Architecture to isolate the core business logic from external infrastructure and tools like web frameworks, databases, and third-party APIs.

This is achieved through three main layers:

1.  **Core / Domain (`app/core`)**: This is the heart of the application. It contains the business logic, rules, and data structures (models) that are independent of any external technology.
    *   `use_cases.py`: Orchestrates the steps required to fulfill a business objective (e.g., `AnalyzeTranscriptUseCase`).
    *   `models.py`: Defines the pure Pydantic models for the application's domain (e.g., `TranscriptAnalysis`).
    *   `exceptions.py`: Contains custom exceptions that represent business errors (e.g., `TranscriptNotFoundError`).

2.  **Ports (`app/ports`)**: These are the interfaces (defined as Abstract Base Classes) that the core logic uses to communicate with the outside world. They act as "contracts" that adapters must fulfill.
    *   `llm.py`: Defines the `LLm` interface, specifying the methods required for any AI language model interaction.
    *   `repository.py`: Defines the `AnalysisRepository` interface for persistence operations (saving and retrieving data).

3.  **Adapters (`app/adapters`)**: These are the concrete implementations of the ports. They are the "pluggable" components that connect the application's core to real-world tools.
    *   `openai.py`: An adapter that implements the `LLm` port by making calls to the OpenAI API.
    *   `persistence.py`: An adapter that implements the `AnalysisRepository` port using a simple in-memory dictionary. This could easily be swapped for a database adapter (e.g., PostgreSQL) without changing any core logic.

### High-Level Solution Diagram

This diagram illustrates the flow of a request through the system, highlighting the separation of concerns.

```
+----------------+      +---------------------+      +------------------------+
|   User/Client  |----->|  FastAPI (Web API)  |----->|   Use Case Factories   |
+----------------+      |   (app/api/*)       |      | (app/api/dependencies) |
                        +----------+----------+      +------------+-----------+
                                   |                             |
     (Dependency Injection)        | Wires up...                 | Provides...
                                   v                             v
                        +---------------------+      +------------------------+
                        |  Use Cases (Core)   |<---->|      Ports (ABCs)      |
                        |   (app/core/*)      |      |      (app/ports/*)       |
                        +---------------------+      +--+------------------+--+
                                                         ^                  ^
                                                         | Implements...    | Implements...
                                                         |                  |
                        +---------------------+      +------------------------+
                        |   In-Memory Repo    |      |    OpenAI API Adapter  |
                        | (app/adapters/...)  |      |   (app/adapters/...)   |
                        +---------------------+      +------------------------+
```

## How to Run the Application

### Prerequisites

*   Python 3.9+
*   An active OpenAI API key

### Setup Instructions

1.  **Clone the Repository**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and Activate a Virtual Environment**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You would need to generate a `requirements.txt` file using `pip freeze > requirements.txt`)*

4.  **Configure Environment Variables**
    The application loads configuration from a `.env` file. You must provide your OpenAI API key here.

    *   Create a new file named `.env` in the root directory.
    *   Add your credentials to it, following the format:
        ```env
        OPENAI_API_KEY="sk-your-actual-openai-api-key-here"
        OPENAI_MODEL="gpt-4o"
        ```

### Running the Server

Use `uvicorn` to run the FastAPI application:

```bash
uvicorn app.api.main:app --reload
```

The `--reload` flag enables hot-reloading for development, so the server will automatically restart after code changes.

The API will be running at `http://127.0.0.1:8000`.

### Accessing the API Documentation

Once the server is running, you can access the interactive Swagger UI documentation in your browser to explore and test the endpoints:

**`http://127.0.0.1:8000/docs`**

## Testing the Application

### Why We Use Mocks (Especially When an OpenAI Key is Not Provided)

In modern software development, tests need to be **fast, reliable, and isolated**. Relying on external services like the OpenAI API during testing violates all of these principles.

1.  **Cost**: Each API call to OpenAI costs money. Running a full test suite frequently could lead to significant, unnecessary expenses.
2.  **Speed**: Network calls are inherently slow. A proper test suite should run in seconds (or even milliseconds), not minutes. Waiting for real API responses would make testing a painfully slow process.
3.  **Reliability & Determinism**: External APIs can fail or experience latency. Their responses might also change unexpectedly. This makes tests "flaky"—they might fail for reasons that have nothing to do with our code's correctness. Mocks provide the same, predictable response every single time, ensuring our tests are deterministic.
4.  **Isolation**: When we test our API endpoints, we want to verify that *our* logic is correct (e.g., Does it handle requests correctly? Does it map errors to the right HTTP status codes?). We do not want to test whether the OpenAI API is working. **By mocking the LLM adapter, we isolate our API layer and test it independently.**

The test `tests/adapters/test_openai.py` is an *integration test* designed to test our actual connection to OpenAI, and it is correctly marked to be skipped if no API key is provided, preventing test failures in environments without secrets.

### How Mocks Are Implemented

The project uses FastAPI's built-in dependency injection system to swap real dependencies with mock objects during testing.

*   In `tests/api/test_endpoints.py`, the `client` fixture uses `app.dependency_overrides`.
*   This feature allows us to replace functions like `get_analyze_transcript_use_case` with a "mock factory" that provides the use case with a `MockLLMAdapter` instead of the real `OpenAIAdapter`.
*   The `MockLLMAdapter` returns a fixed, predictable response, allowing us to assert the API's behavior with confidence.

### Running the Test Suite

To run all automated tests, use `pytest`:

```bash
pytest
```