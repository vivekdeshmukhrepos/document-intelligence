# Import ChatOpenAI to interact with OpenAI's GPT models via LangChain
from langchain.chat_models import ChatOpenAI
# Import ConversationalRetrievalChain to create a chain that combines retrieval and conversation
from langchain.chains import ConversationalRetrievalChain
# Import ConversationBufferMemory to store conversation history for context-aware responses
from langchain.memory import ConversationBufferMemory
# Import Config to access environment variables like API keys securely
from config import Config

# Define LLMService class to encapsulate all LLM-related operations
class LLMService:
    # Initialize LLMService with a vector store for document retrieval
    def __init__(self, vector_store):
        # Create a ChatOpenAI instance to interact with OpenAI's GPT-4 model
        # temperature=0.7 controls creativity (0=deterministic, 1=random), 0.7 is balanced
        # model_name="gpt-4-0613" specifies the GPT-4 model version to use
        # openai_api_key is retrieved from Config to authenticate with OpenAI API
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-4-0613",
            openai_api_key=Config.OPENAI_API_KEY
        )
        # Initialize ConversationBufferMemory to store chat history in memory
        # memory_key="chat_history" specifies the key name for storing conversation messages
        # return_messages=True returns messages as a list instead of a single string
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        # Create a ConversationalRetrievalChain that combines document retrieval with conversation
        # This chain retrieves relevant documents and uses them to answer questions in context
        # llm=self.llm uses our ChatOpenAI instance for generating responses
        # retriever=vector_store.vectore_store.as_retriever() converts vector store to a retriever for document lookup
        # memory=self.memory provides conversation history for context-aware responses
        self.chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=vector_store.vectore_store.as_retriever(),
            memory=self.memory
        )

    # Method to get a response from the LLM based on a user query
    def get_response(self, query):
        # Wrap the logic in a try-except block to handle errors gracefully
        try:
            # Call the conversational retrieval chain with the user's question
            # The chain retrieves relevant documents and generates an answer using GPT-4
            # {"question": query} passes the user query to the chain
            response = self.chain({"question": query})
            # Extract and return the 'answer' field from the response
            # This contains the LLM's generated answer based on retrieved documents
            return response['answer']
        # Catch any exceptions that occur during processing (API errors, retrieval errors, etc.)
        except Exception as e:
            # Log the error message for debugging purposes
            print(f"Error getting LLM response: {e}")
            # Return a user-friendly error message instead of crashing the application
            return "I encountered an error processing your request."