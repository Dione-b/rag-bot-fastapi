import os
import time
from fastapi import HTTPException, UploadFile, File
from dotenv import load_dotenv
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

class PDFService:
    UPLOAD_DIR = "uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    def __init__(self):
        load_dotenv()
        self.embeddings = OpenAIEmbeddings()
        self.retrieval_chain = None

    async def upload_pdf(self, pdf_file: UploadFile = File(...)):
        """
        Esta função realiza o upload de um arquivo do tipo pdf.
        """
        if not pdf_file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="O arquivo fornecido não é um PDF.")
        
        base_name = os.path.splitext(pdf_file.filename)[0]
        unique_id = int(time.time())
        unique_filename = f"{base_name}_{unique_id}.pdf"
        file_path = os.path.join(self.UPLOAD_DIR, unique_filename)

        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await pdf_file.read())
            # Após o upload, chame split_and_vectorize_pdf    
            await self.split_and_vectorize_pdf(file_path)
            return {"filename": unique_filename, "content_type": pdf_file.content_type}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def split_and_vectorize_pdf(self, file_path):
        """
        Divide o pdf em chunks menores e logo em seguida realiza a criação de um banco de vetor.
        """
        loader = PyPDFLoader(file_path=file_path)
        documents = loader.load()

        text_splitter = CharacterTextSplitter(
            chunk_size=1000, chunk_overlap=50, separator="\n"
        )

        docs = text_splitter.split_documents(documents)

        vectorstore = FAISS.from_documents(docs, self.embeddings)
        vectorstore.save_local("vector_db")

        await self.setup_chat_system()

    async def setup_chat_system(self):
        """
        Configura o sistema de chat para recuperação de QA.
        """
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        llm = ChatOpenAI()
        combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
        retriever = FAISS.load_local("vector_db", self.embeddings).as_retriever()
        
        self.retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

    async def ask_question(self, question: str):
        """
        Faz uma pergunta ao sistema de chat e retorna a resposta.
        """
        if self.retrieval_chain is None:
            raise ValueError("O retrieval_chain não foi configurado. Certifique-se de que o sistema de chat foi configurado antes de fazer perguntas.")
        
        response = self.retrieval_chain.invoke({"input": question})
        
        return response["answer"]