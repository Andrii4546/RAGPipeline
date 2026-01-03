#!/bin/bash
# Script to pull the required Ollama model
# Using llama3.1:1b for lower memory requirements (~1.3 GB)
# For more memory, you can use llama3.1:3b or llama3.1:8b

MODEL=${1:-llama3.2:1b}

echo "Pulling Ollama model: $MODEL"
echo "This may take several minutes depending on your internet connection..."
echo ""

docker compose exec ollama ollama pull $MODEL

echo ""
echo "Model pull complete!"
echo "You can now use the RAG API."
echo ""
echo "Note: Make sure LLM_MODEL in docker-compose.yml matches: $MODEL"

