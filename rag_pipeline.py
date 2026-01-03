"""
Complete RAG Pipeline
This module implements a full RAG (Retrieval-Augmented Generation) pipeline that:
1. Loads and processes PDF documents
2. Transcribes audio files using Whisper
3. Chunks text semantically
4. Embeds and stores in Qdrant vector database
5. Retrieves relevant chunks and generates answers using LLM
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import SentenceTransformersTokenTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams
from sentence_transformers import SentenceTransformer
import whisper
import ollama

# Configure Ollama host from environment variable if set
OLLAMA_HOST = os.getenv('OLLAMA_URL', os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
if OLLAMA_HOST:
    # Remove http:// or https:// prefix if present, ollama library handles it
    ollama_host = OLLAMA_HOST.replace('http://', '').replace('https://', '')
    os.environ['OLLAMA_HOST'] = ollama_host


class RAGPipeline:
    """Complete RAG pipeline implementation."""

    PRESENTATION_SPEECH_REFINEMENT_PROMPT = """
        You are given a transcript of a presentation.
        
        Ignore and remove:
        - Technical checks (e.g., "Can you hear me?", "Can you see my screen?")
        - Greetings, small talk, interruptions
        - Filler words and repetitions
        - Audience interaction unrelated to the topic
        
        Focus only on:
        - Key topics and objectives
        - Important explanations and insights
        - Data, metrics, and examples
        - Conclusions, recommendations, and next steps
        
        Do not invent information.
        
        Transcript:
        \"\"\"
        {transcript}
        \"\"\"
        
        Produce:
        1. A concise summary
        2. Bullet-point key takeaways
        """

    PRESENTATION_SPEECH_REFINEMENT_SYSTEM_PROMPT = """
        You are an expert analyst summarizing presentation transcripts.
        Extract only meaningful and important information.
        """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "rag_pipeline",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 20,
        chunk_overlap: int = 0,
        whisper_model: str = "base",
        llm_model: str = "llama3.1:8b"
    ):
        """
        Initialize the RAG pipeline.
        
        Args:
            qdrant_url: URL of Qdrant server
            collection_name: Name of the Qdrant collection
            embedding_model: Name of the sentence transformer model
            chunk_size: Size of text chunks (in tokens)
            chunk_overlap: Overlap between chunks
            whisper_model: Whisper model to use for transcription
            llm_model: Ollama model to use for generation
        """
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model
        self.whisper_model_name = whisper_model
        self.llm_model = llm_model
        
        # Initialize components
        self.embedding_model = SentenceTransformer(embedding_model)
        self.qdrant_client = QdrantClient(url=qdrant_url)
        
        # Initialize text splitter
        self.text_splitter = SentenceTransformersTokenTextSplitter(
            model_name="sentence-transformers/all-mpnet-base-v2",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        
        # Initialize Whisper model (lazy loading)
        self.whisper_model = None
        
        # Create collection if it doesn't exist
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create Qdrant collection if it doesn't exist."""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Get embedding dimension
                test_embedding = self.embedding_model.encode(["test"])
                vector_size = len(test_embedding[0])
                
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection '{self.collection_name}' with vector size {vector_size}")
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")
            raise

    def summarize_transcript(self, transcript: str) -> str:
        response = ollama.generate(
            model=self.llm_model,
            system=self.PRESENTATION_SPEECH_REFINEMENT_SYSTEM_PROMPT,
            prompt=self.PRESENTATION_SPEECH_REFINEMENT_PROMPT.format(transcript=transcript),
            options={
                "temperature": 0.2
            }
        )
        return response["response"]


    def load_pdf(self, pdf_path: str) -> List[str]:
        """
        Load PDF file and extract text content.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of document texts (one per page)
        """
        print(f"Loading PDF from {pdf_path}...")
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Extract text from documents
        texts = [doc.page_content for doc in documents]
        print(f"Extracted {len(documents)} pages from PDF")
        
        return texts
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file using Whisper.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        print(f"Transcribing audio from {audio_path}...")
        
        # Lazy load Whisper model
        if self.whisper_model is None:
            print(f"Loading Whisper model '{self.whisper_model_name}'...")
            self.whisper_model = whisper.load_model(self.whisper_model_name)
        
        # Transcribe audio
        result = self.whisper_model.transcribe(audio_path)
        transcript = result["text"]
        
        print(f"Transcription complete. Length: {len(transcript)} characters")
        return transcript
    
    def chunk_text(self, texts: List[str], source: str = "unknown") -> List[Dict[str, str]]:
        """
        Split text into semantically meaningful chunks.
        
        Args:
            texts: List of text strings to chunk
            source: Source identifier for the text
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        print(f"Chunking {len(texts)} text(s) from source '{source}'...")
        
        all_chunks = []
        
        for idx, text in enumerate(texts):
            # Use split_text for plain text strings
            chunks = self.text_splitter.split_text(text)
            
            # Clean and format chunks
            for chunk_idx, chunk_text in enumerate(chunks):
                # Remove leading numbers (page numbers)
                cleaned_text = re.sub(r"^\d+\s*", "", chunk_text)
                
                all_chunks.append({
                    "text": cleaned_text,
                    "source": source,
                    "original_index": idx,
                    "chunk_index": chunk_idx
                })
        
        print(f"Created {len(all_chunks)} chunks")
        return all_chunks
    
    def embed_and_store(self, chunks: List[Dict[str, str]], start_id: int = 0) -> int:
        """
        Generate embeddings and store in Qdrant.
        
        Args:
            chunks: List of chunk dictionaries
            start_id: Starting ID for points (to avoid conflicts)
            
        Returns:
            Next available ID after storing
        """
        print(f"Generating embeddings for {len(chunks)} chunks...")
        
        # Extract texts for embedding
        texts = [chunk["text"] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts)
        
        # Create points for Qdrant
        points = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            points.append(
                PointStruct(
                    id=start_id + idx,
                    vector=embedding.tolist(),
                    payload={
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "original_index": chunk.get("original_index", 0),
                        "chunk_index": chunk.get("chunk_index", idx)
                    }
                )
            )
        
        # Store in Qdrant
        print(f"Storing {len(points)} points in Qdrant...")
        self.qdrant_client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        print(f"Successfully stored {len(points)} chunks in vector database")
        return start_id + len(points)
    
    def process_pdf(self, pdf_path: str) -> int:
        """
        Complete pipeline for processing a PDF: load, chunk, embed, and store.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Number of chunks stored
        """
        # Load PDF
        pdf_texts = self.load_pdf(pdf_path)
        
        # Chunk text
        chunks = self.chunk_text(pdf_texts, source=os.path.basename(pdf_path))
        
        # Get current collection size to determine start_id
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            start_id = collection_info.points_count
        except:
            start_id = 0
        
        # Embed and store
        next_id = self.embed_and_store(chunks, start_id=start_id)
        
        return len(chunks)
    
    def process_audio(self, audio_path: str) -> int:
        """
        Complete pipeline for processing audio: transcribe, chunk, embed, and store.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Number of chunks stored
        """
        # Transcribe audio
        transcript = self.transcribe_audio(audio_path)

        # Chunk text (treat transcript as single text)
        chunks = self.chunk_text([transcript], source=os.path.basename(audio_path))
        
        # Get current collection size to determine start_id
        try:
            collection_info = self.qdrant_client.get_collection(self.collection_name)
            start_id = collection_info.points_count
        except:
            start_id = 0
        
        # Embed and store
        self.embed_and_store(chunks, start_id=start_id)
        
        return len(chunks)
    
    def retrieve(self, question: str, top_k: int = 5, score_threshold: float = 0.3) -> List[Dict]:
        """
        Retrieve relevant chunks for a question.
        
        Args:
            question: User's question
            top_k: Number of top chunks to retrieve
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of relevant chunks with scores
        """
        # Generate embedding for the question
        question_embedding = self.embedding_model.encode([question])[0]
        
        # Query Qdrant
        search_results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=question_embedding.tolist(),
            limit=top_k,
            with_payload=True
        )
        
        # Filter by score threshold
        relevant_chunks = []
        for point in search_results.points:
            if point.score and point.score >= score_threshold:
                relevant_chunks.append({
                    "text": point.payload.get("text", ""),
                    "source": point.payload.get("source", "unknown"),
                    "score": point.score
                })
        
        return relevant_chunks
    
    def generate_answer(self, question: str, context_chunks: List[Dict]) -> str:
        """
        Generate an answer using LLM with retrieved context.
        
        Args:
            question: User's question
            context_chunks: List of relevant context chunks
            
        Returns:
            Generated answer
        """
        # Format context
        context_text = "\n\n".join([
            f"[Source: {chunk['source']}]\n{chunk['text']}"
            for chunk in context_chunks
        ])
        
        # Create prompt
        prompt = f"""Answer the question using the provided context. If the context does not contain relevant information, say you don't know.

Context:
{context_text}

Question: {question}

Answer:"""
        
        # Generate answer using Ollama
        try:
            response = ollama.generate(
                model=self.llm_model,
                prompt=prompt
            )
            return response['response']
        except Exception as e:
            return f"Error generating answer: {e}"
    
    def query(self, question: str, top_k: int = 5, score_threshold: float = 0.3) -> Dict:
        """
        Complete query pipeline: retrieve relevant chunks and generate answer.
        
        Args:
            question: User's question
            top_k: Number of top chunks to retrieve
            score_threshold: Minimum similarity score threshold
            
        Returns:
            Dictionary with answer and retrieved chunks
        """
        print(f"Processing question: {question}")
        
        # Retrieve relevant chunks
        chunks = self.retrieve(question, top_k=top_k, score_threshold=score_threshold)
        
        if not chunks:
            return {
                "answer": "I couldn't find any relevant information in the knowledge base to answer this question.",
                "chunks": [],
                "num_chunks": 0
            }
        
        print(f"Retrieved {len(chunks)} relevant chunks")
        
        # Generate answer
        answer = self.generate_answer(question, chunks)
        
        return {
            "answer": answer,
            "chunks": chunks,
            "num_chunks": len(chunks)
        }
