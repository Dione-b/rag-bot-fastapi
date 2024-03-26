from fastapi import APIRouter, UploadFile, File, Body, HTTPException, Path
from services import PDFService
import os
from datetime import datetime

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
        pdf_files_info = []
        for f in os.listdir(UPLOAD_DIR):
            if f.endswith('.pdf'):
                file_path = os.path.join(UPLOAD_DIR, f)
                modification_time = os.path.getmtime(file_path)
                modification_date = datetime.fromtimestamp(modification_time)
                formatted_date = modification_date.strftime('%Y-%m-%d %H:%M:%S')
                pdf_files_info.append({"title": f, "modification_date": formatted_date})
        return {"pdfs": pdf_files_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-pdf/{pdf_name}")
async def delete_pdf(pdf_name: str = Path(...)):
    """ Exclui um arquivo PDF da pasta uploads """
    UPLOAD_DIR = "uploads"
    file_path = os.path.join(UPLOAD_DIR, pdf_name)
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            return {"detail": f"O arquivo {pdf_name} foi excluído com sucesso."}
        else:
            raise HTTPException(status_code=404, detail=f"O arquivo {pdf_name} não foi encontrado.")
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