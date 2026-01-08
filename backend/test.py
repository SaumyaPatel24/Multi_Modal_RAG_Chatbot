from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

persistent_directory = "db/chroma_db"

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Open your vector store
db = Chroma(
    persist_directory=persistent_directory,
    embedding_function=embedding_model
)

# Get all stored documents and metadata
# Check DB contents first
vectors = db._collection.get(include=["documents", "metadatas"])
print(f"Vectors in DB: {len(vectors['documents'])}")
print("First document preview:", vectors['documents'][0][:200])

# Test retrieval
retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":3})
question = "Recent work experience and projects of Saumya Patel"
relevant_docs = retriever.invoke(question)
print(f"Retrieved {len(relevant_docs)} documents")
for doc in relevant_docs:
    print(doc.page_content[:200])
