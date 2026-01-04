# HOPE - AI-Powered Panic Attack Support System

> **⚠️ IMPORTANT**: This is a safety-critical healthcare system. All components must undergo clinical review before production deployment.

## Overview

HOPE is a production-grade AI-powered virtual therapist focused specifically on panic attacks. The system is designed to be modular, secure, scalable, and ethically responsible.

### Architecture Principles

- **Clean Architecture**: Domain logic isolated from infrastructure
- **Safety-First**: All AI outputs pass through validation layers
- **Provider-Agnostic**: LLM providers can be swapped without code changes
- **HIPAA-Ready**: Encryption, audit logging, consent management built-in

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend Framework | FastAPI (Python 3.11+) |
| AI/ML | PyTorch, HuggingFace Transformers |
| Database | PostgreSQL with encrypted fields |
| Vector Database | Pinecone / Weaviate |
| LLM Integration | OpenAI / Google Gemini |

## Project Structure

```
hope/
├── src/hope/
│   ├── config/          # Application configuration
│   ├── domain/          # Core business entities
│   ├── infrastructure/  # External integrations (DB, LLM, Vector)
│   ├── services/        # Business logic layer
│   └── api/             # HTTP endpoints
├── alembic/             # Database migrations
└── tests/               # Unit and integration tests
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- API keys for OpenAI/Gemini and Pinecone/Weaviate

### Installation

```bash
# Clone and setup
cd hope
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -e ".[dev]"

# Configure environment
copy .env.example .env
# Edit .env with your credentials

# Run database migrations
alembic upgrade head

# Start the server
uvicorn hope.main:app --reload
```

### API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Safety Pipeline

All AI interactions follow this flow:

```
User Input → Panic Detection → Decision Engine → Prompt Builder → LLM → Safety Validator → Response
```

**Key Safety Features:**
- No direct therapeutic advice from AI
- Medical claim detection and filtering
- Hard constraints on response content
- Full audit trail for all interactions

## Development

```bash
# Run tests
pytest tests/ -v

# Type checking
mypy src/hope --strict

# Linting
ruff check src/hope

# Format code
black src/hope
```

## Clinical Review Markers

Code sections requiring clinical input are marked with:
```python
# CLINICAL_REVIEW_REQUIRED: [description]
```

Search for these markers before production deployment.

## License

Proprietary - All Rights Reserved
