# Complete RAG Pipeline

A comprehensive Retrieval-Augmented Generation (RAG) pipeline that processes PDF documents and audio files, stores them in a vector database, and provides question-answering capabilities.

## Features

- **PDF Processing**: Extract text from PDF documents
- **Audio Transcription**: Transcribe audio files using OpenAI's Whisper
- **Semantic Chunking**: Split text into semantically meaningful chunks
- **Vector Storage**: Store embeddings in Qdrant vector database
- **Retrieval**: Find relevant chunks for user questions
- **Answer Generation**: Generate answers using LLM with retrieved context

## Prerequisites

1. **Qdrant Server**: Make sure Qdrant is running on `http://localhost:6333`
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

2. **Ollama**: Install and run Ollama with a model (e.g., `llama3.1:8b`)
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3.1:8b
   ```

3. **Python Dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

## Installation

1. Clone or navigate to the project directory
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```python
from rag_pipeline import RAGPipeline

# Initialize the pipeline
pipeline = RAGPipeline(
    collection_name="my_rag_collection",
    chunk_size=20,
    chunk_overlap=0
)

# Process a PDF file
pipeline.process_pdf("path/to/document.pdf")

# Process an audio file
pipeline.process_audio("path/to/audio.wav")

# Query the knowledge base
result = pipeline.query("What is RAG?")
print(result["answer"])
```

### Running the Example

```bash
python rag_pipeline.py
```

This will:
1. Process the PDF file from `../Module4/Productized & Enterprise RAG.pdf`
2. Process the audio file from `../Module4/audio.wav`
3. Run example queries

### Custom Configuration

You can customize the pipeline with different models and parameters:

```python
pipeline = RAGPipeline(
    qdrant_url="http://localhost:6333",
    collection_name="custom_collection",
    embedding_model="all-MiniLM-L6-v2",  # or other sentence transformer models
    chunk_size=30,                        # Adjust chunk size
    chunk_overlap=5,                      # Add overlap between chunks
    whisper_model="base",                 # or "small", "medium", "large"
    llm_model="llama3.1:8b"              # or other Ollama models
)
```

## Pipeline Components

### 1. Data Loading
- **PDF**: Uses `PyPDFLoader` from LangChain to extract text
- **Audio**: Uses OpenAI's Whisper for transcription

### 2. Text Chunking
- Uses `SentenceTransformersTokenTextSplitter` for semantic chunking
- Preserves context by splitting at semantically meaningful boundaries

### 3. Embedding Generation
- Uses Sentence Transformers (default: `all-MiniLM-L6-v2`)
- Converts text chunks into 384-dimensional vectors

### 4. Vector Storage
- Stores embeddings in Qdrant with metadata (source, indices)
- Automatically creates collection if it doesn't exist

### 5. Retrieval
- Converts questions to embeddings
- Searches for similar chunks using cosine similarity
- Filters results by similarity score threshold

### 6. Answer Generation
- Combines retrieved context with the question
- Uses Ollama LLM to generate answers
- Handles cases where no relevant context is found

## API Reference

### RAGPipeline Class

#### Methods

- `load_pdf(pdf_path)`: Load and extract text from PDF
- `transcribe_audio(audio_path)`: Transcribe audio to text
- `chunk_text(texts, source)`: Split text into semantic chunks
- `embed_and_store(chunks, start_id)`: Generate embeddings and store in Qdrant
- `process_pdf(pdf_path)`: Complete PDF processing pipeline
- `process_audio(audio_path)`: Complete audio processing pipeline
- `retrieve(question, top_k, score_threshold)`: Retrieve relevant chunks
- `generate_answer(question, context_chunks)`: Generate answer with LLM
- `query(question, top_k, score_threshold)`: Complete query pipeline

## REST API

The pipeline includes a REST API server for easy integration.

### Starting the API Server

```bash
python rag_api.py
```

The server will start on `http://localhost:5002`

### API Endpoints

- `GET /health` - Health check
- `POST /upload/pdf` - Upload and process PDF files
- `POST /upload/media` - Upload and process audio/video files
- `POST /query` - Answer questions (JSON body)
- `GET /answer` - Answer questions (query parameters)

See `API_DOCUMENTATION.md` for detailed API documentation.

### Testing the API

```bash
python test_api.py
```

## File Structure

```
Module4Cursor/
├── rag_pipeline.py      # Main RAG pipeline implementation
├── rag_api.py          # REST API server
├── test_api.py         # API test script
├── example_usage.py    # Example usage script
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── API_DOCUMENTATION.md # API documentation
```

## Troubleshooting

1. **Qdrant Connection Error**: Make sure Qdrant is running on `http://localhost:6333`
2. **Ollama Error**: Ensure Ollama is running and the model is downloaded
3. **Whisper Model Download**: First run may download the Whisper model (can take time)
4. **Memory Issues**: Use smaller Whisper models (`base` instead of `large`) for lower memory usage

## Notes

- The first time you run the pipeline, Whisper will download the model (can be several GB)
- Make sure you have sufficient disk space for model downloads
- Qdrant collection is created automatically if it doesn't exist
- Chunks are stored with metadata including source file and indices

