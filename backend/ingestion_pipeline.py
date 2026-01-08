import json
import os
from typing import List

from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title


from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

"""Partition Docs->Atomic Elements"""
def partition_document(file_path: str):
    elements = partition_pdf(
        filename=file_path,
        strategy="hi_res",
        infer_table_structure=True,
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True
    )

    print(f"Partitioned document into {len(elements)} elements.")
    return elements

"""Elements -> Compsite Chunks by Title"""
def create_chunks_by_title(elements):
    chunks = chunk_by_title(
        elements,
        max_characters=3000,
        new_after_n_chars=2400,
        combine_text_under_n_chars=500
    )
    print(f"Created {len(chunks)} chunks by title.")
    for i, chunk in enumerate(chunks):
        if hasattr(chunk, "text"):
            print(f"Chunk {i+1} has {len(chunk.text)} characters, type(chunk.text) = {type(chunk.text)}")
        else:
            print(f"Chunk {i+1} is not a text element, type = {type(chunk)}; value = {chunk}")
    return chunks

"""Chunk -> Seperates into text, tables, images"""
def seperate_chunk(chunk):
    content = {
        "text": chunk.text,
        "tables":[],
        "images": [],
        "types": []
    }

    if hasattr(chunk, 'metadata') and hasattr(chunk.metadata, 'orig_elements'):
        for element in chunk.metadata.orig_elements:
            element_type = type(element).__name__

            if element_type == "Table":
                content["types"].append("table")
                table_html = getattr(element.metadata, 'text_as_html', element.text)
                content["tables"].append(table_html)
            elif element_type == "Image":
                if hasattr(element, 'metadata') and hasattr(element.metadata, 'image_base64'):
                    content["types"].append("image")
                    base64_img = element.metadata.image_base64
                    content["images"].append(base64_img)
    content["types"] = list(set(content["types"]))
    return content


"""Each chunk -> Summary Text by feeding chunk content into LLM"""
def summary_text(text: str, tables: List[str], images: List[str]) -> str:
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
        prompt = f"""Generate a concise summary for the following content:
        
        Text Content:
        {text}
        
        """
        if tables:
            prompt += f"Tables present:\n"
            for i, table in enumerate(tables, start=1):
                prompt += f"Table {i}:\n{table}\n\n"
        
        prompt += """
        YOUR TASK:
        Generate a comprehensive, searchable description that covers:

        1. Key facts, numbers, and data points from text and tables
        2. Main topics and concepts discussed  
        3. Questions this content could answer
        4. Visual content analysis (charts, diagrams, patterns in images)
        5. Alternative search terms users might use

        Make it detailed and searchable - prioritize findability over brevity.

        SEARCHABLE DESCRIPTION:"""
            
        message = [{"type": "text", "text": prompt}]

        for img in images:
            message.append({"type": "image_url", "image_url": f"data:image/jpeg;base64,{img}"})

        response = llm.invoke([HumanMessage(content=message)])
        
        summary = response.content
        return summary
    
    except Exception as e:
        print(f"Error generating summary: {e}")
        return ""


""" Process Chunks to Langchain Documents with Summaries"""
def process_chunks_to_docs(chunks):
    langchain_docs = []

    total_chunks = len(chunks)

    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{total_chunks}")
        content = seperate_chunk(chunk)

        if content["tables"] or content["images"]:
            try:
                enhanced_content = summary_text(content["text"], content["tables"], content["images"])
            except Exception as e:  
                print(f"Error generating summary for chunk {i+1}: {e}")
                enhanced_content = ""
        
        else:
            enhanced_content = content["text"]
        
        doc = Document(
            page_content=enhanced_content,
            metadata={
                "Original_content": json.dumps(content)
            }
        )

        langchain_docs.append(doc)
        print(doc)
    print(f"Processed {len(langchain_docs)} chunks into Langchain Documents.")
    return langchain_docs


def complete_ingestion_pipeline(file_path: str, persist_directory="db/chroma_db"):
    # Step 1: Partition Document
    elements = partition_document(file_path)

    # Step 2: Create Chunks by Title
    chunks = create_chunks_by_title(elements)

    # Step 3: Process Chunks to Langchain Documents (used helper methods summary_text and seperate_chunk)
    langchain_docs = process_chunks_to_docs(chunks)

    # Step 4: Create Vector Store
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = Chroma.from_documents(
        documents=langchain_docs,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_metadata={"hnsw:space": "cosine"}
    )
    print(f"Vector store created and persisted at '{persist_directory}'.")
    

    

