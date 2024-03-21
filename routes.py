from fastapi import APIRouter, UploadFile, File, Body, HTTPException
from services import PDFService
import os

router = APIRouter()

pdf_service = PDFService()

@router.post("/upload/pdf/")
async def upload_pdf(pdf_file: UploadFile = File(...)):
    """ Realiza o upload do PDF """
    return await pdf_service.upload_pdf(pdf_file)

@router.get("/split/{pdf_name}")
async def split_pdf(pdf_name: str):
    """ Realiza o split e vetorização do PDF """
    UPLOAD_DIR = "uploads"
    file_path = os.path.join(UPLOAD_DIR, pdf_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo PDF não encontrado")
    
    try:
        await pdf_service.split_and_vectorize_pdf(file_path)
        return {"message": "Vetor salvo com sucesso."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/list-pdfs")
async def list_pdfs():
    """ Lista todos os PDF salvos em disco """
    UPLOAD_DIR = "uploads"
    try:
        pdf_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.pdf')]
        return {"pdfs": pdf_files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/")
async def chat(question: dict = Body(...)):
    """ Interage com o PDF através de uma pergunta. """
    try:
        question = question.get("question")
        
        if not question:
            raise ValueError("A pergunta não foi fornecida")
        
        answer = await pdf_service.ask_question(question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))