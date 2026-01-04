import json
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv

# ok now i have complete igestion pipeline-> stores enhanced chunks in vector db
# and retireval pipeline-> generates answer from history.

load_dotenv()

persistent_directory = "db/chroma_db"

embedding_model = OpenAIEmbeddings(model ="text-embedding-3-small", openai_api_key=os.getenv("OPENAI_API_KEY"))

db = Chroma(
    persist_directory=persistent_directory,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"}
)



def complete_retrieval_pipeline(question, chat_history):
    # Reformulate question based on chat history
    previous_qs = [chat["text"] for chat in chat_history if chat["type"] == "user"]
    if len(previous_qs) > 1:
        messages = [
            SystemMessage(content="Create a new standalone question from the conversation history and the current question.")
            ]+previous_qs+[
            HumanMessage(content=question)]
        
        model = ChatOpenAI(model ="gpt-4o-mini" , openai_api_key=os.getenv("OPENAI_API_KEY"))
        new_question = model.invoke(messages).content
        print(f"Reformulated Question: {new_question}")
    else:
        new_question = question
    

    # retrieve chunks from the vector database
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":3})
    relevant_docs = retriever.invoke(new_question)
    
    # create combined input for the model
    try:
        # invoking the model to get the answer for combined input
        model = ChatOpenAI(model ="gpt-4o-mini" , openai_api_key=os.getenv("OPENAI_API_KEY"))

        prompt_text  = f"""Based on the following documents, please answer the question: {new_question}
        Document:
        """
        
        for i, doc in enumerate(relevant_docs):
            prompt_text += f"--- Document {i+1} ---\n"

            if "original_content" in doc.metadata:
                original_content = json.loads(doc.metadata["Original_content"])
                raw_text = original_content.get("text", "")
                if raw_text:
                    prompt_text += f"Text: \n{raw_text}\n\n"
                
                tables = original_content.get("tables", [])
                if tables:
                    prompt_text += "Tables:\n"
                    for j, table in enumerate(tables):
                        prompt_text += f"Table {j+1}:\n{table}\n"
                
                prompt_text += "\n"

        prompt_text += """Please provide a clear, comprehensive answer using the text, tables, and images above. If the documents don't contain sufficient information to answer the question, say "I don't have enough information to answer that question based on the provided documents. ANSWER:"""

        message = [{"text": "text", "text": prompt_text}]

        for doc in relevant_docs:
            if "original_content" in doc.metadata:
                original_content = json.loads(doc.metadata["Original_content"])    
                images = original_content.get("images", [])
                if images:
                    for image_base64 in enumerate(images):
                        message.append({"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_base64}"})

        message = [HumanMessage(content=message)]
        response = model.invoke([message])

           
        print("Response from the model:")
        result = response.content
        return result
    
    except Exception as e:
        print(f"Error during retrieval pipeline: {e}")
        return "An error occurred while processing your request."
    