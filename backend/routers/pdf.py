"""
PDF router - Upload, list, delete, and summarize PDFs
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import uuid
import aiofiles
from pathlib import Path

from database.connection import get_db
from database.models import User, PDF as PDFModel
from auth.middleware import get_current_user
from services.rag_service import rag_service
from services.groq_client import groq_client

router = APIRouter(prefix="/pdf", tags=["PDF Management"])


# Pydantic models
class PDFResponse(BaseModel):
    id: str
    file_id: str
    filename: str
    upload_date: str
    total_chunks: int
    file_size: int


class UploadResponse(BaseModel):
    pdf: PDFResponse
    message: str


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and index a PDF document"""
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    file_path = Path("uploads") / f"{file_id}.pdf"
    
    try:
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_size = len(content)
        
        # Index in ChromaDB
        index_result = await rag_service.index_document(
            user_id=str(current_user.id),
            file_id=file_id,
            file_path=str(file_path)
        )
        
        if not index_result.get("success"):
            file_path.unlink()  # Delete file
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to index PDF: {index_result.get('error')}"
            )
        
        # Save to database
        pdf_record = PDFModel(
            user_id=current_user.id,
            file_id=file_id,
            filename=file.filename,
            file_path=str(file_path),
            total_chunks=index_result.get("total_chunks", 0),
            file_size=file_size
        )
        
        db.add(pdf_record)
        db.commit()
        db.refresh(pdf_record)
        
        return {
            "pdf": {
                "id": str(pdf_record.id),
                "file_id": pdf_record.file_id,
                "filename": pdf_record.filename,
                "upload_date": pdf_record.upload_date.isoformat(),
                "total_chunks": pdf_record.total_chunks,
                "file_size": pdf_record.file_size
            },
            "message": f"PDF uploaded and indexed with {index_result.get('total_chunks')} chunks"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Cleanup on error
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/list", response_model=List[PDFResponse])
async def list_pdfs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all PDFs for the current user"""
    pdfs = db.query(PDFModel).filter(PDFModel.user_id == current_user.id).all()
    
    return [
        {
            "id": str(pdf.id),
            "file_id": pdf.file_id,
            "filename": pdf.filename,
            "upload_date": pdf.upload_date.isoformat(),
            "total_chunks": pdf.total_chunks,
            "file_size": pdf.file_size
        }
        for pdf in pdfs
    ]


@router.post("/summarize/{pdf_id}")
async def summarize_pdf(
    pdf_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate summary of PDF using Groq"""
    # Get PDF record
    pdf = db.query(PDFModel).filter(
        PDFModel.id == pdf_id,
        PDFModel.user_id == current_user.id
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    # Get document context
    context = await rag_service.get_document_context(
        user_id=str(current_user.id),
        file_id=pdf.file_id,
        top_k=15  # More chunks for better summary
    )
    
    # Generate summary using Groq
    summary = await groq_client.summarize_document(context)
    
    return {
        "pdf_id": pdf_id,
        "filename": pdf.filename,
        "summary": summary
    }


@router.delete("/{pdf_id}")
async def delete_pdf(
    pdf_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a PDF and all its data"""
    # Get PDF record
    pdf = db.query(PDFModel).filter(
        PDFModel.id == pdf_id,
        PDFModel.user_id == current_user.id
    ).first()
    
    if not pdf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF not found"
        )
    
    # Delete from ChromaDB
    await rag_service.delete_document(
        user_id=str(current_user.id),
        file_id=pdf.file_id
    )
    
    # Delete file
    file_path = Path(pdf.file_path)
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database (cascades to chats, quizzes)
    db.delete(pdf)
    db.commit()
    
    return {"message": "PDF deleted successfully"}
