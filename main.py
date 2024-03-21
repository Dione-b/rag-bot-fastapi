from fastapi import FastAPI
from routes import router as pdf_router

app = FastAPI()

app.include_router(pdf_router)