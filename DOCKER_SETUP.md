# Docker Setup Guide

This guide explains how to run the RAG Pipeline using Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

1. **Start the services:**
   ```bash
   docker-compose up -d
   ```

2. **Pull the required Ollama model (first time only):**
   ```bash
   docker-compose exec ollama ollama pull llama3.1:8b
   ```
   
   Or use a smaller model for faster startup:
   ```bash
   docker-compose exec ollama ollama pull llama3.1:1b
   ```
   
   Then update `LLM_MODEL` in `docker-compose.yml` if using a different model.

2. **Check service status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f rag_api
   docker-compose logs -f qdrant
   ```

4. **Stop the services:**
   ```bash
   docker-compose down
   ```

5. **Stop and remove volumes (clean slate):**
   ```bash
   docker-compose down -v
   ```

## Services

### Qdrant Database
- **Container:** `rag_qdrant`
- **Ports:**
  - `6333` - REST API
  - `6334` - gRPC API
- **Web UI:** http://localhost:6333/dashboard
- **Storage:** Persistent volume `qdrant_storage`

### Ollama LLM Service
- **Container:** `rag_ollama`
- **Port:** `11434`
- **API:** http://localhost:11434
- **Storage:** Persistent volume `ollama_data`
- **Note:** Models need to be pulled before first use: `docker-compose exec ollama ollama pull llama3.1:8b`

### RAG API
- **Container:** `rag_api`
- **Port:** `5002`
- **API:** http://localhost:5002
- **Health Check:** http://localhost:5002/health

## Configuration

### Environment Variables

You can customize the setup by modifying `docker-compose.yml` or using environment variables:

**RAG API Environment Variables:**
- `QDRANT_URL` - Qdrant service URL (default: `http://qdrant:6333`)
- `OLLAMA_HOST` - Ollama service host (default: `ollama:11434`)
- `COLLECTION_NAME` - Vector database collection name (default: `rag_pipeline`)
- `CHUNK_SIZE` - Text chunk size in tokens (default: `20`)
- `CHUNK_OVERLAP` - Overlap between chunks (default: `0`)
- `WHISPER_MODEL` - Whisper model size: `tiny`, `base`, `small`, `medium`, `large` (default: `base`)
- `LLM_MODEL` - Ollama model name (default: `llama3.1:8b`)
- `FLASK_ENV` - Flask environment: `production` or `development` (default: `production`)
- `FLASK_HOST` - Flask host (default: `0.0.0.0`)
- `FLASK_PORT` - Flask port (default: `5002`)

### Volumes

- `qdrant_storage` - Persistent storage for Qdrant data
- `uploads` - Temporary storage for file uploads
- `./models` - Whisper models cache (mapped to host)

## Building

### Build the RAG API image:
```bash
docker-compose build rag_api
```

### Rebuild without cache:
```bash
docker-compose build --no-cache rag_api
```

## Usage Examples

### 1. Check Health
```bash
curl http://localhost:5002/health
```

### 2. Upload PDF
```bash
curl -X POST http://localhost:5002/upload/pdf \
  -F "file=@document.pdf"
```

### 3. Upload Audio
```bash
curl -X POST http://localhost:5002/upload/media \
  -F "file=@audio.wav"
```

### 4. Query
```bash
curl -X POST http://localhost:5002/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

## Troubleshooting

### Service won't start

1. **Check logs:**
   ```bash
   docker-compose logs rag_api
   docker-compose logs qdrant
   ```

2. **Check if ports are available:**
   ```bash
   # Check if ports 5002, 6333, 6334 are in use
   lsof -i :5002
   lsof -i :6333
   lsof -i :6334
   ```

3. **Verify Docker is running:**
   ```bash
   docker ps
   ```

### Qdrant connection issues

- Ensure Qdrant service is healthy: `docker-compose ps`
- Check Qdrant logs: `docker-compose logs qdrant`
- Verify network connectivity: The API uses `http://qdrant:6333` (service name) inside Docker

### Model download issues

- Whisper models are downloaded on first use (can take time)
- Models are cached in the `./models` volume
- For faster startup, pre-download models or use a smaller model (`tiny` or `base`)

### Memory issues

- Whisper models can be memory-intensive
- Use smaller models (`tiny`, `base`) for limited resources
- Increase Docker memory limits if needed

## Development

### Run in development mode

1. Edit `docker-compose.yml` and set:
   ```yaml
   environment:
     - FLASK_ENV=development
   ```

2. Rebuild and restart:
   ```bash
   docker-compose up -d --build
   ```

### Access container shell

```bash
# RAG API container
docker-compose exec rag_api bash

# Qdrant container
docker-compose exec qdrant sh
```

### View Qdrant dashboard

Open http://localhost:6333/dashboard in your browser to view:
- Collections
- Points
- Search interface

## Production Considerations

1. **Security:**
   - Don't expose ports publicly without authentication
   - Use reverse proxy (nginx, traefik) with SSL
   - Implement API authentication

2. **Performance:**
   - Use larger Whisper models for better accuracy
   - Adjust chunk sizes based on your documents
   - Consider GPU support for faster processing

3. **Persistence:**
   - Qdrant data is stored in `qdrant_storage` volume
   - Backup volumes regularly
   - Consider external storage for production

4. **Monitoring:**
   - Set up health checks
   - Monitor resource usage
   - Log aggregation

## Cleanup

### Remove everything (including volumes):
```bash
docker-compose down -v
```

### Remove only containers:
```bash
docker-compose down
```

### Remove images:
```bash
docker rmi module4cursor-rag_api
docker rmi qdrant/qdrant
```

