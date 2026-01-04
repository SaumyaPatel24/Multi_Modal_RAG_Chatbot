from fastapi import FastAPI, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ingestion_pipeline import complete_ingestion_pipeline
from retrieval_pipeline import complete_retrieval_pipeline

app = FastAPI()

# connects frontend and backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    try:
        file_location = f"docs/{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        
        # Call the ingestion pipeline
        complete_ingestion_pipeline(file_location)
        return JSONResponse(content={"message": f"File '{file.filename}' ingested successfully."})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    
@app.post("/query")
async def get_answer(request: Request):
    data = await request.json()
    question = data.get("question")
    chat_history = data.get("chat_history", [])
    try:
        answer = complete_retrieval_pipeline(question, chat_history)
        return JSONResponse(content={"answer": answer})
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/")
async def root():
    return {"message": "RAG backend is running!"}