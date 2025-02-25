from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import uuid

from app.bot.rag_chain import RAGChain
from app.utils.pdf_processor import PDFProcessor

router = APIRouter(prefix="/api", tags=["rag"])

# Models for request/response
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class PDFInfo(BaseModel):
    filename: str
    path: str

class PDFListResponse(BaseModel):
    pdfs: List[PDFInfo]

# Create instances
pdf_processor = PDFProcessor()
rag_chain = None

def get_rag_chain():
    global rag_chain
    if rag_chain is None:
        rag_chain = RAGChain()
    return rag_chain

@router.post("/upload-pdfs", response_model=List[str])
async def upload_pdfs(
    files: List[UploadFile] = File(...),
    rag_chain: RAGChain = Depends(get_rag_chain)
):
    """Upload PDF files and process them for RAG."""
    if not files:
        raise HTTPException(status_code=400, detail="No PDF files provided")
    
    # Save the PDFs
    saved_paths = await pdf_processor.save_uploaded_pdfs(files)
    
    if not saved_paths:
        raise HTTPException(status_code=400, detail="No valid PDF files were uploaded")
    
    # Load PDFs into the RAG chain
    rag_chain.load_pdfs(saved_paths)
    
    return saved_paths

@router.get("/pdfs", response_model=PDFListResponse)
async def get_pdfs():
    """Get a list of all available PDFs."""
    pdfs = pdf_processor.get_saved_pdfs()
    return PDFListResponse(pdfs=pdfs)

@router.delete("/pdfs/{filename}")
async def delete_pdf(
    filename: str,
    rag_chain: RAGChain = Depends(get_rag_chain)
):
    """Delete a specific PDF file."""
    success = pdf_processor.delete_pdf(filename)
    
    if not success:
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    # Reload the PDFs without the deleted one
    pdfs = pdf_processor.get_saved_pdfs()
    if pdfs:
        rag_chain.load_pdfs([pdf["path"] for pdf in pdfs])
    
    return {"status": "success", "message": f"PDF {filename} deleted successfully"}

@router.delete("/pdfs")
async def delete_all_pdfs(
    rag_chain: RAGChain = Depends(get_rag_chain)
):
    """Delete all PDF files."""
    success = pdf_processor.delete_all_pdfs()
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete PDFs")
    
    # Clear the RAG chain
    rag_chain.clear_all_sessions()
    
    return {"status": "success", "message": "All PDFs deleted successfully"}

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_chain: RAGChain = Depends(get_rag_chain)
):
    """Chat with the RAG model."""
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG chain not initialized")
    
    # Generate or use session ID
    session_id = request.session_id or str(uuid.uuid4())
    
    # Process the message
    response = rag_chain.query(request.message, session_id)
    
    return ChatResponse(response=response, session_id=session_id)

@router.delete("/chat/{session_id}")
async def clear_chat_history(
    session_id: str,
    rag_chain: RAGChain = Depends(get_rag_chain)
):
    """Clear chat history for a specific session."""
    rag_chain.clear_session(session_id)
    
    return {"status": "success", "message": f"Chat history for session {session_id} cleared"}