"""
REST API for RAG Pipeline
Provides endpoints to upload PDF/media files and answer questions.
"""

import os
import tempfile
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from rag_pipeline import RAGPipeline

app = Flask(__name__)

# Configuration from environment variables
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'wav', 'mp3', 'mp4', 'm4a', 'flac', 'ogg'}

# Get configuration from environment variables
QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'rag_api_collection')
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '20'))
CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '0'))
WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
LLM_MODEL = os.getenv('LLM_MODEL', 'llama3.1:8b')

# Initialize RAG Pipeline
pipeline = RAGPipeline(
    qdrant_url=QDRANT_URL,
    collection_name=COLLECTION_NAME,
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    whisper_model=WHISPER_MODEL,
    llm_model=LLM_MODEL
)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'RAG Pipeline API'
    }), 200


@app.route('/upload/pdf', methods=['POST'])
def upload_pdf():
    """
    Upload and process a PDF file.
    
    Request:
        - Method: POST
        - Content-Type: multipart/form-data
        - Body: file (PDF file)
    
    Response:
        - 200: Success with number of chunks processed
        - 400: Bad request (no file or invalid file)
        - 500: Server error
    """
    if 'file' not in request.files:
        return jsonify({
            'error': 'No file part in the request',
            'message': 'Please provide a file in the "file" field'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'error': 'No file selected',
            'message': 'Please select a file to upload'
        }), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({
            'error': 'Invalid file type',
            'message': 'Only PDF files are allowed'
        }), 400
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Process PDF
        num_chunks = pipeline.process_pdf(filepath)
        
        # Clean up temporary file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'PDF processed successfully',
            'filename': filename,
            'chunks_processed': num_chunks
        }), 200
    
    except Exception as e:
        # Clean up on error
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'error': 'Processing failed',
            'message': str(e)
        }), 500


@app.route('/upload/media', methods=['POST'])
def upload_media():
    """
    Upload and process a media file (audio/video).
    Supported formats: wav, mp3, mp4, m4a, flac, ogg
    
    Request:
        - Method: POST
        - Content-Type: multipart/form-data
        - Body: file (audio/video file)
    
    Response:
        - 200: Success with number of chunks processed
        - 400: Bad request (no file or invalid file)
        - 500: Server error
    """
    if 'file' not in request.files:
        return jsonify({
            'error': 'No file part in the request',
            'message': 'Please provide a file in the "file" field'
        }), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({
            'error': 'No file selected',
            'message': 'Please select a file to upload'
        }), 400
    
    if not allowed_file(file.filename):
        return jsonify({
            'error': 'Invalid file type',
            'message': f'Allowed formats: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Process media file (transcribe and store)
        num_chunks = pipeline.process_audio(filepath)
        
        # Clean up temporary file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Media file processed successfully',
            'filename': filename,
            'chunks_processed': num_chunks
        }), 200
    
    except Exception as e:
        # Clean up on error
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'error': 'Processing failed',
            'message': str(e)
        }), 500


@app.route('/query', methods=['POST'])
def query():
    """
    Answer a question using the RAG pipeline.
    
    Request:
        - Method: POST
        - Content-Type: application/json
        - Body: {
            "question": "Your question here",
            "top_k": 5 (optional, default: 5),
            "score_threshold": 0.3 (optional, default: 0.3)
          }
    
    Response:
        - 200: Success with answer and metadata
        - 400: Bad request (missing question)
        - 500: Server error
    """
    if not request.is_json:
        return jsonify({
            'error': 'Invalid content type',
            'message': 'Content-Type must be application/json'
        }), 400
    
    data = request.get_json()
    
    if not data or 'question' not in data:
        return jsonify({
            'error': 'Missing question',
            'message': 'Please provide a "question" field in the request body'
        }), 400
    
    question = data['question'].strip()
    
    if not question:
        return jsonify({
            'error': 'Empty question',
            'message': 'Question cannot be empty'
        }), 400
    
    try:
        # Get optional parameters
        top_k = data.get('top_k', 5)
        score_threshold = data.get('score_threshold', 0.3)
        
        # Query the pipeline
        result = pipeline.query(
            question=question,
            top_k=top_k,
            score_threshold=score_threshold
        )
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': result['answer'],
            'num_chunks_retrieved': result['num_chunks'],
            'chunks': [
                {
                    'text': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text'],
                    'source': chunk['source'],
                    'score': round(chunk['score'], 4)
                }
                for chunk in result['chunks']
            ]
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Query failed',
            'message': str(e)
        }), 500


@app.route('/answer', methods=['GET'])
def answer_question():
    """
    Answer a question using GET method (for convenience).
    
    Request:
        - Method: GET
        - Query parameters:
            - question: The question to answer (required)
            - top_k: Number of chunks to retrieve (optional, default: 5)
            - score_threshold: Minimum similarity score (optional, default: 0.3)
    
    Response:
        - 200: Success with answer
        - 400: Bad request (missing question)
        - 500: Server error
    """
    question = request.args.get('question')
    
    if not question:
        return jsonify({
            'error': 'Missing question',
            'message': 'Please provide a "question" query parameter'
        }), 400
    
    question = question.strip()
    
    if not question:
        return jsonify({
            'error': 'Empty question',
            'message': 'Question cannot be empty'
        }), 400
    
    try:
        # Get optional parameters
        top_k = request.args.get('top_k', 5, type=int)
        score_threshold = request.args.get('score_threshold', 0.3, type=float)
        
        # Query the pipeline
        result = pipeline.query(
            question=question,
            top_k=top_k,
            score_threshold=score_threshold
        )
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': result['answer'],
            'num_chunks_retrieved': result['num_chunks'],
            'chunks': [
                {
                    'text': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text'],
                    'source': chunk['source'],
                    'score': round(chunk['score'], 4)
                }
                for chunk in result['chunks']
            ]
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Query failed',
            'message': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("RAG Pipeline REST API")
    print("=" * 60)
    print(f"Qdrant URL: {QDRANT_URL}")
    print(f"Collection name: {COLLECTION_NAME}")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Chunk size: {CHUNK_SIZE}")
    print(f"Whisper model: {WHISPER_MODEL}")
    print(f"LLM model: {LLM_MODEL}")
    print("\nAvailable endpoints:")
    print("  GET  /health - Health check")
    print("  POST /upload/pdf - Upload and process PDF file")
    print("  POST /upload/media - Upload and process media file")
    print("  POST /query - Answer question (JSON body)")
    print("  GET  /answer - Answer question (query parameter)")
    
    # Get host and port from environment or use defaults
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5002'))
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    print(f"\nStarting server on http://{host}:{port}")
    print("=" * 60)
    
    app.run(debug=debug, host=host, port=port)

