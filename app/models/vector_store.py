# Import chromadb - a vector database library for storing and retrieving embeddings
# chromadb is lightweight, open-source, and designed for semantic search on embeddings
import chromadb 
# Import Chroma from LangChain - a wrapper that integrates chromadb with LangChain framework
# This provides seamless integration with LangChain's document processing pipeline
from langchain.vectorstores import Chroma
# Import OpenAIEmbeddings to convert text into vector embeddings using OpenAI's models
# Embeddings transform text into numerical vectors that capture semantic meaning
from langchain.embeddings.openai import OpenAIEmbeddings


# Define VectorStore class to manage document embeddings and similarity search
class VectorStore:
    # Initialize VectorStore with a path to persist embeddings on disk
    def __init__(self, path):
        # Create an OpenAIEmbeddings instance to convert documents to vector embeddings
        # This uses OpenAI's embedding models to represent text as numerical vectors
        # The embeddings capture semantic meaning, allowing similarity-based search
        self.embeddings = OpenAIEmbeddings()
        # Initialize a Chroma vector store with persistent storage
        # persist_directory=path specifies where to save embeddings on disk for later retrieval
        # embedding_function=self.embeddings tells Chroma which embedding model to use
        # Chroma stores these embeddings in an efficient format optimized for similarity search
        self.vectore_store = Chroma(
            persist_directory=path,
            embedding_function=self.embeddings
        )

    
    # Method to add documents to the vector store
    def add_documents(self, documents):
        # Convert documents to embeddings and store them in the vector database
        # This makes the documents searchable via semantic similarity search later
        # The documents parameter should be a list of LangChain Document objects
        self.vectore_store.add_documents(documents)
    

    # Method to search for similar documents based on a query
    def similarity_search(self, query, k=4):
        # Convert the query to an embedding and find the k most similar documents
        # k=4 is the default number of similar documents to return (can be overridden)
        # This uses vector distance (e.g., cosine similarity) to find semantically related documents
        # Returns a list of Document objects that are most similar to the query
        return self.vectore_store.similarity_search(query, k=k)



