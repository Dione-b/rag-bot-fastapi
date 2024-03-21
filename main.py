from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as pdf_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite requisições de qualquer lugar (temporário)
    allow_credentials=True,
    allow_methods=["*"], # Permite todos os métodos HTTP
    allow_headers=["*"], # Permite todos os cabeçalhos
)

app.include_router(pdf_router)