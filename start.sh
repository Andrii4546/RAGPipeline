#!/bin/bash
# Complete startup script for RAG Pipeline

echo "=========================================="
echo "Starting RAG Pipeline Services"
echo "=========================================="

# Step 1: Start all containers
echo ""
echo "Step 1: Starting Docker containers..."
docker-compose up -d

# Wait for Ollama to be ready
echo ""
echo "Step 2: Waiting for Ollama service to be ready..."
sleep 10

# Step 2: Check if model exists, if not pull it
echo ""
echo "Step 3: Checking for Ollama model..."
MODEL_EXISTS=$(docker-compose exec -T ollama ollama list 2>/dev/null | grep -q "llama3.1:8b" && echo "yes" || echo "no")

if [ "$MODEL_EXISTS" = "no" ]; then
    echo "Model 'llama3.1:8b' not found. Pulling it now..."
    echo "This may take several minutes depending on your internet connection..."
    docker-compose exec ollama ollama pull llama3.1:8b
    echo ""
    echo "✓ Model downloaded successfully!"
else
    echo "✓ Model 'llama3.1:8b' already exists!"
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Services are running:"
echo "  - Qdrant:    http://localhost:6333"
echo "  - Ollama:    http://localhost:11434"
echo "  - RAG API:   http://localhost:5002"
echo ""
echo "Check status: docker-compose ps"
echo "View logs:    docker-compose logs -f"
echo ""

