# AI Teaching Companion MVP

This project is a Minimum Viable Product (MVP) for an AI Teaching Companion system. It consists of a backend built with Python and Flask, providing APIs for student and teacher-facing applications. The system uses a multi-agent architecture conceptually, with different Python classes representing these agents.

## Project Overview

The system aims to:
- Allow students to log their learning activities.
- Provide students with an analysis of their strengths and weaknesses based on their activities and a predefined syllabus.
- Allow teachers to view student progress, activity summaries, and strengths/weaknesses analyses.

**Core Components:**
- **Student Interaction Agent (`agents/student_interaction_agent.py`):** Manages data and logic for an individual student, including loading a syllabus, logging activities, and performing basic analysis.
- **Teacher Data Aggregator Agent (`agents/teacher_data_aggregator_agent.py`):** Collects data from multiple student agents for the teacher.
- **Teacher Console Agent (`agents/teacher_console_agent.py`):** Provides an interface (currently programmatic) for teacher interactions, utilizing the aggregator.
- **Student Service API (`student_service_app.py`):** A Flask app that exposes endpoints for student-related actions (e.g., logging activity, getting dashboard data).
- **Teacher Service API (`teacher_service_app.py`):** A Flask app that exposes endpoints for teacher-related actions (e.g., listing students, getting individual student summaries).
- **API Tests (`tests/test_api_endpoints.py`):** `unittest`-based tests for the Flask API endpoints.

## Directory Structure

```
.
├── agents/
│   ├── student_interaction_agent.py  # Logic for individual student agent
│   ├── teacher_data_aggregator_agent.py # Aggregates data from student agents
│   ├── teacher_console_agent.py      # Teacher's interface to the aggregator
│   └── sample_syllabus.json          # Default syllabus used by the agents
├── tests/
│   └── test_api_endpoints.py         # Automated tests for the API services
├── student_service_app.py            # Flask API service for student interactions
├── teacher_service_app.py            # Flask API service for teacher interactions
└── README.md                         # This file
```

## Setup and Installation

1.  **Clone the repository (if applicable).**
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install Flask requests
    ```

## Running the Services

The backend consists of two main Flask services that need to be run independently.

1.  **Start the Student Service:**
    Open a terminal and run:
    ```bash
    python student_service_app.py
    ```
    This service will typically start on `http://localhost:5001`.

2.  **Start the Teacher Service:**
    Open another terminal and run:
    ```bash
    python teacher_service_app.py
    ```
    This service will typically start on `http://localhost:5000`.

Ensure both services are running before attempting to use the APIs fully or running the automated tests.

## Running the API Tests

With both services (Student and Teacher) running in separate terminals:

1.  Open a third terminal.
2.  Navigate to the project's root directory.
3.  Run the tests using Python's `unittest` module:
    ```bash
    python -m unittest tests.test_api_endpoints
    ```
    Or, if you are in the `tests` directory:
    ```bash
    python test_api_endpoints.py
    ```

The tests will make live HTTP calls to the running services and report successes or failures.

## Current State & Next Steps

- The core agent logic and API services for MVP functionalities are in place.
- The `get_strengths_weaknesses` method in `student_interaction_agent.py` has been recently updated with more nuanced logic.
- **Immediate Next Step:** Update API tests in `tests/test_api_endpoints.py` to reflect the changes in the strengths/weaknesses logic.

## Future Development Ideas
- More sophisticated NLP for Q&A and resource recommendation.
- Advanced performance tracking and early warning systems for teachers.
- Integration with a persistent database instead of in-memory storage.
- User authentication and authorization.
- Development of the actual Android front-end applications.
- More robust inter-agent communication (e.g., message queues).
```
