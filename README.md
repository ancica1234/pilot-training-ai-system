# ✈️ Aviation Training Multi-Agent System

A multi-agent AI system for aviation flight training management built with LangGraph, Groq LLaMA 3.3, FastAPI, and Streamlit.

## Architecture

```
User Query
    ↓
Supervisor (LLM routing + Python keyword guard rails)
    ↓
┌─────────────┬───────────┬─────────────┬─────────────────┬─────────────────────────┐
│  Scheduler  │ Evaluator │ Remediation │ Risk Assessment │ Instructor Notification │
│  📅         │ 📊        │ 🔧          │ ⚠️              │ 📨                      │
└─────────────┴───────────┴─────────────┴─────────────────┴─────────────────────────┘
    ↓
Human-in-the-Loop Approval (before notifications)
    ↓
FastAPI REST API / Streamlit UI
```

## Features

- **5 specialist agents** — each with its own tools and scope
- **LLM supervisor** with Python keyword guard rails preventing out-of-scope agent calls
- **Human-in-the-loop interrupts** — graph pauses before sending instructor notifications for human approval
- **FastAPI REST API** with Pydantic validation and interactive Swagger UI
- **Streamlit web UI** with tabbed interface for queries, student status, and notification log
- **LangSmith observability** — full trace visibility of LLM calls and agent decisions
- **86 pytest tests** covering tools, routing logic, data integrity, and API endpoints

## Agents

| Agent | Tools | Responsibility |
|---|---|---|
| Scheduler | `get_class_schedule`, `get_student_history`, `get_class_students` | Class schedules and student event history |
| Evaluator | `evaluate_progress` | Student progress assessment |
| Remediation | `get_remediation_plan`, `recommend_best_option` | Remediation plan generation |
| Risk Assessment | `assess_risk`, `compare_student_risks` | Individual and class-wide risk scoring |
| Instructor Notification | `send_instructor_alert`, `get_instructor_for_class` | Instructor alerts with human approval |

## Tech Stack

- **LangGraph** — multi-agent orchestration and graph state management
- **Groq LLaMA 3.3 70B** — LLM for supervisor routing and agent reasoning
- **FastAPI** — REST API with Pydantic validation
- **Streamlit** — web UI
- **LangSmith** — LLM observability and tracing
- **pytest** — unit and integration testing

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key
export GROQ_API_KEY=your_key_here

# Run CLI
python main.py

# Run Streamlit UI
streamlit run streamlit_app.py

# Run FastAPI
uvicorn api.main:app --reload
# Then open http://localhost:8000/docs

# Run tests
python -m pytest
```

## Optional: LangSmith Tracing

```bash
export LANGSMITH_API_KEY=your_key_here
# Traces appear at https://smith.langchain.com
```

## Example Queries

1. `Evaluate John Smith's training progress and assess his risk level.`
2. `Compare risk levels for all students in class 25-4.`
3. `Build a remediation plan for John Smith, assess his risk, then notify his instructor.`
4. `Give me a full status report on class 25-5 and alert the instructor about any high-risk students.`

## Project Structure

```
├── agents/                  # Specialist agents and their tools
│   ├── scheduler.py
│   ├── evaluator.py
│   ├── remediation.py
│   ├── risk_assessment.py
│   └── instructor_notification.py
├── api/                     # FastAPI REST API
│   ├── main.py
│   └── models.py
├── data/
│   └── mock_data.py         # Mock student and class data
├── graph/
│   └── graph.py             # LangGraph graph definition and supervisor
├── tests/                   # pytest test suite (86 tests)
│   ├── test_api.py
│   ├── test_data.py
│   ├── test_routing.py
│   └── test_tools.py
├── main.py                  # CLI entry point
├── streamlit_app.py         # Streamlit web UI
└── README.md
```
