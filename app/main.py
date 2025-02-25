import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.routes import router as api_router
from app.bot.rag_chain import RAGChain

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="RAG PDF Chatbot API",
    description="API for chatting with PDF documents using Retrieval Augmented Generation",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Initialize RAG chain on startup
@app.on_event("startup")
async def startup_event():
    # Initialize the RAG chain with the API key from environment variables
    RAGChain()

@app.get("/")
async def root():
    return {
        "message": "Welcome to the RAG PDF Chatbot API",
        "documentation": "/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)