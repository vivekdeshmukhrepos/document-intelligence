# Import ChatOpenAI to interact with OpenAI's GPT models via LangChain
from langchain_openai import ChatOpenAI
# Import BaseMessage types for handling chat messages
from langchain_core.messages import HumanMessage, AIMessage
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
        
        # Store the vector store for document retrieval
        self.vector_store = vector_store
        
        # Store conversation history as a list of messages for context
        # This allows the LLM to maintain conversation context across multiple queries
        self.chat_history = []

    # Method to get a response from the LLM based on a user query
    def get_response(self, query):
        # Wrap the logic in a try-except block to handle errors gracefully
        try:
            # Search the vector store for relevant document chunks
            # This retrieves the k=4 most similar documents to the query
            relevant_docs = self.vector_store.similarity_search(query, k=4)
            
            # Extract the content from the retrieved documents to use as context
            context = "\n".join([doc.page_content for doc in relevant_docs])
            
            # Build the conversation history as a string for inclusion in the prompt
            chat_history_str = "\n".join([
                f"User: {msg.content}" if isinstance(msg, HumanMessage) else f"Assistant: {msg.content}"
                for msg in self.chat_history
            ])
            
            # Create the prompt for the LLM that includes context and conversation history
            prompt_text = f"""
You are a helpful AI assistant. Use the following context from documents to answer the user's question.
If the context doesn't contain relevant information, say so honestly.

Context:
{context}

Chat History:
{chat_history_str}

Question: {query}

Answer:"""
            
            # Call the LLM with the prompt
            # The LLM returns a response based on the context and chat history
            response = self.llm.invoke(prompt_text)
            
            # Extract the response content
            # The invoke method returns a message object, so we need to access its content
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Add the user query and assistant response to chat history
            # This maintains conversation context for future queries
            self.chat_history.append(HumanMessage(content=query))
            self.chat_history.append(AIMessage(content=response_text))
            
            # Return the LLM's generated response
            return response_text.strip()
        # Catch any exceptions that occur during processing (API errors, retrieval errors, etc.)
        except Exception as e:
            # Log the error message for debugging purposes
            print(f"Error getting LLM response: {e}")
            # Return a user-friendly error message instead of crashing the application
            return "I encountered an error processing your request."