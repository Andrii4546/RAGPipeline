# RAG Pipeline REST API Documentation

## Base URL
```
http://localhost:5002
```

## Endpoints

### 1. Health Check
Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "RAG Pipeline API"
}
```

---

### 2. Upload PDF
Upload and process a PDF file. The PDF will be loaded, chunked, embedded, and stored in the vector database.

**Endpoint:** `POST /upload/pdf`

**Content-Type:** `multipart/form-data`

**Request Body:**
- `file` (required): PDF file to upload

**Example using curl:**
```bash
curl -X POST http://localhost:5002/upload/pdf \
  -F "file=@document.pdf"
```

**Example using Python requests:**
```python
import requests

url = "http://localhost:5002/upload/pdf"
files = {"file": open("document.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "PDF processed successfully",
  "filename": "document.pdf",
  "chunks_processed": 45
}
```

**Error Response (400):**
```json
{
  "error": "No file part in the request",
  "message": "Please provide a file in the \"file\" field"
}
```

---

### 3. Upload Media
Upload and process an audio/video file. The file will be transcribed using Whisper, chunked, embedded, and stored in the vector database.

**Endpoint:** `POST /upload/media`

**Content-Type:** `multipart/form-data`

**Supported Formats:** wav, mp3, mp4, m4a, flac, ogg

**Request Body:**
- `file` (required): Audio/video file to upload

**Example using curl:**
```bash
curl -X POST http://localhost:5002/upload/media \
  -F "file=@audio.wav"
```

**Example using Python requests:**
```python
import requests

url = "http://localhost:5002/upload/media"
files = {"file": open("audio.wav", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Media file processed successfully",
  "filename": "audio.wav",
  "chunks_processed": 23
}
```

**Error Response (400):**
```json
{
  "error": "Invalid file type",
  "message": "Allowed formats: wav, mp3, mp4, m4a, flac, ogg"
}
```

---

### 4. Query (POST)
Answer a question using the RAG pipeline. This endpoint accepts JSON in the request body.

**Endpoint:** `POST /query`

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "question": "What is RAG?",
  "top_k": 5,
  "score_threshold": 0.3
}
```

**Parameters:**
- `question` (required): The question to answer
- `top_k` (optional): Number of chunks to retrieve (default: 5)
- `score_threshold` (optional): Minimum similarity score (default: 0.3)

**Example using curl:**
```bash
curl -X POST http://localhost:5002/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?", "top_k": 5}'
```

**Example using Python requests:**
```python
import requests

url = "http://localhost:5002/query"
data = {
    "question": "What is RAG?",
    "top_k": 5,
    "score_threshold": 0.3
}
response = requests.post(url, json=data)
print(response.json())
```

**Success Response (200):**
```json
{
  "success": true,
  "question": "What is RAG?",
  "answer": "RAG stands for Retrieval-Augmented Generation...",
  "num_chunks_retrieved": 5,
  "chunks": [
    {
      "text": "RAG is a technique that combines...",
      "source": "document.pdf",
      "score": 0.8542
    }
  ]
}
```

**Error Response (400):**
```json
{
  "error": "Missing question",
  "message": "Please provide a \"question\" field in the request body"
}
```

---

### 5. Answer (GET)
Answer a question using GET method (for convenience). Same functionality as POST /query but uses query parameters.

**Endpoint:** `GET /answer`

**Query Parameters:**
- `question` (required): The question to answer
- `top_k` (optional): Number of chunks to retrieve (default: 5)
- `score_threshold` (optional): Minimum similarity score (default: 0.3)

**Example using curl:**
```bash
curl "http://localhost:5002/answer?question=What%20is%20RAG?&top_k=5"
```

**Example using Python requests:**
```python
import requests

url = "http://localhost:5002/answer"
params = {
    "question": "What is RAG?",
    "top_k": 5,
    "score_threshold": 0.3
}
response = requests.get(url, params=params)
print(response.json())
```

**Success Response (200):**
```json
{
  "success": true,
  "question": "What is RAG?",
  "answer": "RAG stands for Retrieval-Augmented Generation...",
  "num_chunks_retrieved": 5
}
```

---

## Error Responses

All endpoints may return the following error responses:

**400 Bad Request:**
```json
{
  "error": "Error description",
  "message": "Detailed error message"
}
```

**404 Not Found:**
```json
{
  "error": "Not found",
  "message": "The requested endpoint does not exist"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Processing failed",
  "message": "Error details"
}
```

---

## Complete Example Workflow

```python
import requests

BASE_URL = "http://localhost:5002"

# 1. Check health
response = requests.get(f"{BASE_URL}/health")
print("Health:", response.json())

# 2. Upload PDF
with open("document.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/upload/pdf",
        files={"file": f}
    )
    print("PDF Upload:", response.json())

# 3. Upload audio
with open("audio.wav", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/upload/media",
        files={"file": f}
    )
    print("Media Upload:", response.json())

# 4. Ask a question
response = requests.post(
    f"{BASE_URL}/query",
    json={
        "question": "What are the key components of RAG?",
        "top_k": 5
    }
)
print("Answer:", response.json())
```

---

## Notes

- Files are temporarily stored during processing and automatically deleted afterward
- The API uses the same vector database collection for all uploaded documents
- Make sure Qdrant is running on `http://localhost:6333`
- Make sure Ollama is running with the configured model (default: `llama3.1:8b`)
- First audio transcription may take longer as Whisper downloads the model

