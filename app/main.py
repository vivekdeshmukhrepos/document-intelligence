# Import VectorStore to manage document embeddings and semantic search
from models.vector_store import VectorStore
# Import S3Storage for uploading and retrieving files from AWS S3
from services.storage_service import S3Storage
# Import LLMService to generate responses using OpenAI's GPT model
from services.llm_service import LLMService
# Import Config to access environment variables and configuration settings
from config import Config
# Import os for file system operations like path handling and file removal
import os 
# Import document loaders from LangChain Community for reading PDF and text files
from langchain_community.document_loaders import TextLoader, PyPDFLoader 
# Import RecursiveCharacterTextSplitter from the text_splitters package
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Import tempfile to create temporary directories for processing uploaded files
import tempfile
# Import logging for tracking application events and debugging
import logging
# Import Flask components to build the web API and handle HTTP requests
from flask import Flask, request, render_template, jsonify


# Create a Flask application instance - the main web server for handling HTTP requests
app = Flask(__name__)


# Initialize VectorStore with the configured database path for storing document embeddings
# This allows semantic search on uploaded documents
vector_store = VectorStore(Config.VECTOR_DB_PATH)
# Initialize S3Storage to handle file uploads and downloads from AWS S3
storage_service = S3Storage()
# Initialize LLMService with the vector store to enable question-answering based on documents
llm_service = LLMService(vector_store)


# Define the root route that serves the main web interface
@app.route('/')
def index():
    # Return the index.html template to display the UI in the browser
    return render_template('index.html')

# Configure logging to track application events, errors, and debug information
# DEBUG level shows all log messages from lowest to highest severity
logging.basicConfig(level=logging.DEBUG)
# Create a logger instance for this module to log events
logger = logging.getLogger(__name__)


# Helper function to process uploaded documents into text chunks
def process_document(file):
    """
    Process document based on file type and return text chunks for embedding.
    
    Supports:
    - PDF files: Extracted using PyPDFLoader
    - TXT files: Loaded using TextLoader
    
    Args:
        file: The uploaded file object from Flask request
        
    Returns:
        List of LangChain Document objects split into manageable chunks
        
    Raises:
        ValueError: If file type is not supported (not .pdf or .txt)
    """
    # Create a temporary directory to store the file during processing
    # This directory will be cleaned up after processing is complete
    temp_dir = tempfile.mkdtemp()
    # Create the full path for the temporary file (directory + filename)
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # Save the uploaded file to the temporary location
        # This is necessary because loaders need a file path, not a file object
        file.save(temp_path)
        
        # Process the file based on its extension to extract content
        if file.filename.endswith('.pdf'):
            # Use PyPDFLoader for PDF files - extracts text from all pages
            loader = PyPDFLoader(temp_path)
            documents = loader.load()
        elif file.filename.endswith('.txt'):
            # Use TextLoader for plain text files
            loader = TextLoader(temp_path)
            documents = loader.load()
        else:
            # Raise error if file type is not supported
            raise ValueError("Unsupported file type")

        # Split documents into smaller chunks for better embedding and retrieval
        # Large documents can cause issues with embeddings, so we break them into pieces
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Each chunk is max 1000 characters
            chunk_overlap=200  # Overlap of 200 chars to maintain context between chunks
        )
        # Apply the splitter to break documents into overlapping chunks
        text_chunks = text_splitter.split_documents(documents)
        
        # Return the processed text chunks ready for embedding
        return text_chunks
        
    finally:
        # Clean up temporary files regardless of success or failure
        # This ensures no temporary files are left behind on disk
        if os.path.exists(temp_path):
            os.remove(temp_path)
        os.rmdir(temp_dir)

# Define the API endpoint for uploading and processing documents
@app.route('/upload', methods=['POST'])
def upload_document():
    """
    Handle document upload, process it, store on S3, and add to vector database.
    
    This endpoint:
    1. Validates the uploaded file
    2. Processes the document into chunks
    3. Uploads the original file to S3
    4. Stores the chunks in the vector database for semantic search
    
    Returns:
        JSON response with success message or error details
    """
    try:
        # Log the endpoint call for debugging and monitoring
        logger.debug("Upload endpoint called")
        
        # Check if a file was provided in the request
        if 'file' not in request.files:
            logger.warning("No file in request")
            # Return 400 Bad Request error if no file is provided
            return jsonify({'error': 'No file provided'}), 400
        
        # Get the file from the request
        file = request.files['file']
        # Check if the filename is empty (user selected but didn't choose a file)
        if file.filename == '':
            logger.warning("Empty filename")
            # Return 400 Bad Request error if filename is empty
            return jsonify({'error': 'No file selected'}), 400

        # Validate that the file has a supported extension (.txt or .pdf)
        if not file.filename.endswith(('.txt', '.pdf')):
            logger.warning(f"Unsupported file type: {file.filename}")
            # Return 400 Bad Request error for unsupported file types
            return jsonify({'error': 'Only .txt and .pdf files are supported'}), 400

        # Log the file being processed
        logger.debug(f"Processing file: {file.filename}")
        
        # Process the document: extract content and split into chunks
        try:
            text_chunks = process_document(file)
            logger.debug(f"Document processed into {len(text_chunks)} chunks")
        except Exception as e:
            # Log any errors that occur during document processing
            logger.error(f"Error processing document: {str(e)}")
            # Return 500 Internal Server Error if processing fails
            return jsonify({'error': f'Error processing document: {str(e)}'}), 500

        # Upload the original file to S3 for long-term storage and archival
        try:
            file.seek(0)  # Reset file pointer to beginning for re-reading
            storage_service.upload_file(file, file.filename)
            logger.debug("File uploaded to S3")
        except Exception as e:
            # Log any S3 upload errors
            logger.error(f"Error uploading to S3: {str(e)}")
            # Return 500 Internal Server Error if S3 upload fails
            return jsonify({'error': f'Error uploading to S3: {str(e)}'}), 500

        # Add the processed text chunks to the vector store for semantic search
        # This allows users to query the document content using natural language
        try:
            vector_store.add_documents(text_chunks)
            logger.debug("Documents added to vector store")
        except Exception as e:
            # Log any errors that occur when adding to vector store
            logger.error(f"Error adding to vector store: {str(e)}")
            # Return 500 Internal Server Error if vector store update fails
            return jsonify({'error': f'Error adding to vector store: {str(e)}'}), 500

        # Return success response with the number of chunks processed
        return jsonify({
            'message': 'File uploaded and processed successfully',
            'chunks_processed': len(text_chunks)
        })

    except Exception as e:
        # Catch any unexpected errors not caught by specific handlers
        logger.error(f"Unexpected error: {str(e)}")
        # Return 500 Internal Server Error for unexpected failures
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

# Define the API endpoint for querying documents with natural language questions
@app.route('/query', methods=['POST'])
def query():
    """
    Handle user queries against uploaded documents using semantic search and LLM.
    
    This endpoint:
    1. Receives a natural language question from the user
    2. Searches the vector store for relevant document chunks
    3. Uses GPT-4 to generate an answer based on the retrieved documents
    
    Returns:
        JSON response with the LLM's answer or error details
    """
    # Get the JSON request data containing the user's question
    data = request.json
    # Validate that a question was provided
    if 'question' not in data:
        # Return 400 Bad Request if no question is provided
        return jsonify({'error': 'No question provided'}), 400

    try:
        # Call the LLM service to generate a response
        # The service will:
        # 1. Convert the question to an embedding
        # 2. Search vector store for similar document chunks
        # 3. Use GPT-4 to generate an answer based on those chunks
        response = llm_service.get_response(data['question'])
        # Return the response as JSON
        return jsonify({'response': response})
    except Exception as e:
        # Catch and return any errors that occur during query processing
        return jsonify({'error': str(e)}), 500

# Main entry point - runs the Flask application
if __name__ == '__main__':
    # Start the Flask development server
    # host='0.0.0.0' makes the server accessible from any IP address (not just localhost)
    # port=8080 specifies the port number for the web server
    # debug=True enables auto-reload on code changes and detailed error messages
    app.run(host='0.0.0.0', port=8080, debug=True)