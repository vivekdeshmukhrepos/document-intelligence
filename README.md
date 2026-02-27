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
OPENAI_API_KEY=sk-proj-your-key
AWS_ACCESS_KEY=your-key
AWS_SECRET_KEY=your-secret
AWS_BUCKET_NAME=your-bucket

# Run
python ./app/main.py
# Visit http://localhost:8080
```

## Architecture

```
Flask Server (Port 8080)
├── LLMService (GPT-4, Temperature 0.7)
├── VectorStore (ChromaDB + OpenAI Embeddings)
├── S3Storage (AWS boto3)
└── Web UI (HTML/CSS/JS)

Data Flow:
Upload → Extract Text → Split (1000 chars, 200 overlap)
       → Embed (OpenAI API, 1536 dims) → Store (ChromaDB)
       
Query → Embed → Search (k=4 similarity) → Context
      → Build Prompt → GPT-4 → Response
```

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

## API Endpoints

### GET `/`
Serves web UI

### POST `/upload`
Upload PDF/TXT files
```bash
curl -X POST -F "file=@doc.pdf" http://localhost:8080/upload
```
Response: `{"message": "Document processed successfully"}`

### POST `/query`
Ask questions
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?"}'
```
Response: `{"response": "The document discusses..."}`

## Configuration

**Model Settings** (config.py):
- Model: GPT-4-0613 (8K context window)
- Temperature: 0.7 (balanced creativity)
- Similarity Search K: 4 documents
- Chunk Size: 1000 chars
- Chunk Overlap: 200 chars

**Environment Variables**:
```env
OPENAI_API_KEY           # OpenAI API authentication
AWS_ACCESS_KEY           # AWS IAM access key
AWS_SECRET_KEY           # AWS IAM secret key
AWS_BUCKET_NAME          # S3 bucket for document storage
VECTOR_DB_PATH           # ChromaDB persistent storage path
```

## Project Structure

```
app/
├── main.py              # Flask app, route handlers, document processing
├── config.py            # Configuration from environment
├── models/
│   └── vector_store.py  # ChromaDB wrapper, semantic search
├── services/
│   ├── llm_service.py   # GPT-4 integration, conversation management
│   └── storage_service.py # AWS S3 file operations
├── templates/
│   └── index.html       # Modern web UI with chat interface
├── static/
│   └── style.css        # Responsive styling, animations
└── .env                 # API keys (not committed)
```

## Key Components

### VectorStore (vector_store.py)
```python
class VectorStore:
    __init__(path)              # Init ChromaDB + OpenAI embeddings
    add_documents(documents)    # Embed and store text chunks
    similarity_search(query, k) # Find k nearest neighbors (cosine similarity)
```

### LLMService (llm_service.py)
```python
class LLMService:
    __init__(vector_store)      # Init GPT-4, chat history
    get_response(query)         # 1) Search vectors
                                # 2) Build context from top-k
                                # 3) Call GPT-4 with history
                                # 4) Return response
```

### Storage Service (storage_service.py)
```python
class S3Storage:
    upload_file(file_obj, filename)  # Upload to S3 bucket
    get_file(filename)               # Download from S3
```

## Processing Pipeline

### Document Upload
```
Validate → Extract Text → Chunk (RecursiveCharacterTextSplitter)
→ Generate Embeddings (1536-dim vectors) → Store in ChromaDB
→ Upload original to S3 → Return success
```

**Performance**: Single PDF ~2-5s, 10-page doc ~10-15s

### Question Answering
```
Query → Embedding → Vector Search (cosine similarity)
→ Retrieve top-4 chunks → Build context string
→ Create prompt [system + history + context + question]
→ GPT-4 inference → Update chat history → Response

Typical latency: 5-15 seconds
```

### Semantic Search
Uses cosine similarity in 1536-dimensional space:
- Question → Embedding → Find k similar chunks
- Chunks ranked by similarity scores (0-1)
- Top-k used as context for LLM

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| PDF extraction | 1-3s | Page count dependent |
| Embedding generation | ~100ms/chunk | API latency |
| Similarity search | 100-500ms | DB size dependent |
| GPT-4 inference | 2-5s | Prompt complexity |
| Full Q&A cycle | 5-15s | All components combined |

## Deployment

### Development
```bash
python ./app/main.py
# Auto-reload, debug mode enabled
```

### Production
```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8080 app.main:app
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8080", "app.main:app"]
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError: langchain_text_splitters | `pip install langchain-text-splitters` |
| OPENAI_API_KEY not set | Create `app/.env` with valid key |
| S3 upload fails | Verify AWS credentials, IAM S3 permissions |
| ChromaDB errors | Check disk space, verify write permissions |
| Slow responses | Reduce SIMILARITY_SEARCH_K, check OpenAI quota |
| PDF extraction fails | Use text-based PDFs, not scanned images |

## Security

- ✅ API keys in `.env` (never commit)
- ✅ Input validation (file types, HTML escaping)
- ✅ Environment variable management
- ✅ AWS IAM roles recommended for production
- ✅ No telemetry or data collection

## Dependencies

**Core**:
- flask 2.3.3
- langchain, langchain-core, langchain-community, langchain-openai
- langchain-chroma, langchain-text-splitters
- chromadb, openai, numpy 1.26.4

**Document Processing**:
- pypdf, unstructured, python-dotenv

**Cloud**:
- boto3, botocore

**Utilities**:
- pydantic, tiktoken, requests

## Features

✅ Multi-format document upload (PDF, TXT)  
✅ Semantic similarity search  
✅ GPT-4 context-aware Q&A  
✅ Conversation memory  
✅ AWS S3 cloud storage  
✅ ChromaDB vector persistence  
✅ Modern responsive web UI  
✅ Drag-drop file upload  
✅ Real-time chat interface  
✅ Error handling & logging  

## Future Enhancements

- [ ] Support DOCX, PPT formats
- [ ] User authentication & multi-user
- [ ] Document management (delete/update)
- [ ] Advanced filters & search
- [ ] Export conversations
- [ ] Analytics dashboard
- [ ] Unit/integration tests
- [ ] CI/CD pipeline

## Resources

- [OpenAI API Docs](https://platform.openai.com/docs)
- [LangChain Docs](https://python.langchain.com)
- [ChromaDB Docs](https://docs.trychroma.com)
- [AWS S3 Docs](https://docs.aws.amazon.com/s3)
- [Flask Docs](https://flask.palletsprojects.com)

---

**Status**: Production Ready | **Version**: 1.0 | **Updated**: Feb 2026