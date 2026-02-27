# Document Intelligence System

AI-powered document Q&A platform using semantic search and LLMs. Upload PDFs/TXT files, ask questions, get contextual answers powered by GPT-4.

## Quick Start

```bash
# Setup
python -m venv docint
docint\Scripts\activate  # Windows
source docint/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Configure
# Create app/.env with:
# Get OPENAI_API_KEY from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-your-key

# Get AWS keys from: https://console.aws.amazon.com/iam/home#/users
# Navigate to: IAM → Users → Create New → Enable Console Access → Get Access Keys
AWS_ACCESS_KEY=your-key
AWS_SECRET_KEY=your-secret

# Create S3 bucket from: https://s3.console.aws.amazon.com/s3/home
AWS_BUCKET_NAME=your-bucket

# Run
python ./app/main.py
# Visit http://localhost:8080
```

## Features

✨ **Core Features**
- Multi-format upload (PDF, TXT)
- Semantic similarity search
- AI-powered Q&A with GPT-4
- Cloud storage (AWS S3)
- Vector embeddings (ChromaDB)
- Conversation memory & chat history


## Tech Stack

| Component | Tech | Version |
|-----------|------|---------|
| Framework | Flask | 2.3.3 |
| LLM | LangChain + OpenAI | Latest |
| Embeddings | OpenAI API | text-embedding-3-small |
| Vector DB | ChromaDB | 0.4.x+ |
| Storage | AWS S3 | boto3 |
| Parsing | pypdf + unstructured | Latest |
| Python | 3.8+ | 3.13 tested |


## Project Structure

```
├───app
│   │   config.py
│   │   main.py
│   │   __init__.py
│   │
│   ├───doc_int_vector_db
│   │       chroma.sqlite3
│   │
│   ├───models
│   │   │   vector_store.py
│   │   │   __init__.py
│   │
│   ├───services
│   │   │   llm_service.py
│   │   │   storage_service.py
│   │   │   __init__.py
│   │
│   ├───static
│   │       style.css
│   │
│   ├───ui
│   │       index.html
│
├───data
│        RAG-White-Paper.pdf
│
│   Demo.PNG
│   README.md
│   requirements.txt
│   Steps.txt
```
---

**Status**: Production Ready | **Version**: 1.0 | **Updated**: Feb 2026