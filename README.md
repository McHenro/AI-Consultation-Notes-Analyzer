# AI Notes Analyzer

AI Notes Analyzer is a backend service that uses Large Language Models (LLMs) to transform unstructured professional notes into structured, actionable insights.

It is designed as a production-style backend system, combining:
- Django REST APIs
- Celery background workers
- Redis message broker
- OpenAI’s GPT-5 Responses API

The system asynchronously analyzes notes and returns:
- A concise summary
- Key points
- Missing information
- Suggested next actions

---

## Why this project exists

Modern teams generate large volumes of unstructured notes — medical consultations, support tickets, legal memos, meeting transcripts.  
Manually extracting insights from them is slow, inconsistent, and error-prone.

This project demonstrates how AI can be embedded into real backend systems to automate this analysis reliably, safely, and at scale.

---

## Architecture

Client
↓
Django REST API
↓
PostgreSQL / SQLite
↓
Celery (Redis broker)
↓
OpenAI GPT-5 (Responses API)

The API never blocks while AI is running.  
All AI work happens asynchronously in background workers.

---

## Workflow

1. Client submits a note via API  
2. Django stores the request in the database  
3. A Celery worker picks up the job  
4. The worker sends the note to OpenAI  
5. The AI returns structured JSON  
6. The result is validated, parsed, and stored  
7. The client retrieves the final result via API  

---

## Example Input

```json
{
  "raw_text": "Client reports headaches for 5 days, mild nausea, poor sleep, no fever."
}

```

## Example AI Output
```json
{
  "summary": "The client has experienced headaches and mild nausea for five days with poor sleep and no fever.",
  "key_points": [
    "Headaches lasting 5 days",
    "Mild nausea",
    "Poor sleep",
    "No fever"
  ],
  "missing_information": [
    "Severity of headaches",
    "Any medication taken",
    "Past medical history"
  ],
  "suggested_next_actions": [
    "Ask about pain severity and triggers",
    "Check for medication usage",
    "Consider further evaluation if symptoms persist"
  ]
}
```

---

## Reliability & Safety

This project is built like a real production system:

- Asynchronous processing with Celery
- Automatic retries with exponential backoff
- Strict JSON-only AI prompts
- Defensive parsing of AI responses
- No blocking API calls
- Failure isolation (AI errors do not crash the API)
- Cost control via token limits and lightweight models

---

## Security

- API keys are stored in .env
- .env and database files are ignored by Git
- No secrets are committed to the repository

---

## Tech Stack

- Python 3.11
- Django + Django REST Framework
- Celery
- Redis
- PostgreSQL / SQLite
- OpenAI GPT-5 Responses API

---

## Why this matters

This project demonstrates how a backend engineer can:

- Integrate modern LLMs into production systems
- Design asynchronous, fault-tolerant workflows
- Handle unreliable external APIs
- Build AI-powered services that scale

This is not a chatbot.
It is an AI-enabled backend system.
