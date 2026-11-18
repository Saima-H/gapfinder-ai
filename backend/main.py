from fastapi import FastAPI, Header, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine, Base
from models import Material, Topic, DocumentChunk, Quiz, Question
from jose import jwt
import os
from dotenv import load_dotenv
import io
from pypdf import PdfReader
from openai import OpenAI

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- HELPER FUNCTIONS ---

def get_user_email(authorization: str):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(
            token, 
            os.getenv("SUPABASE_JWT_SECRET"), 
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        user_email = payload.get("email")
        if not user_email:
            raise Exception("No email in token")
        return user_email
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Token")

def process_and_embed_pdf(file_content: bytes, material_id: int, db):
    # 1. Read PDF
    pdf = PdfReader(io.BytesIO(file_content))
    full_text = ""
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
        
    # 2. Chunking (Split into ~1000 character chunks)
    # Using a simple newline splitting for now
    chunks = [c.strip() for c in full_text.split("\n\n") if len(c.strip()) > 50]
    
    # 3. Generate Embeddings and Save to DB
    for chunk in chunks:
        # Call OpenAI to get the 1536-dimension vector
        response = client.embeddings.create(
            input=chunk,
            model="text-embedding-3-small"
        )
        embedding_vector = response.data[0].embedding
        
        # Save to our DocumentChunk table
        new_chunk = DocumentChunk(
            material_id=material_id,
            content=chunk,
            embedding=embedding_vector
        )
        db.add(new_chunk)
    
    db.commit()


# --- ENDPOINTS ---

@app.get("/")
def read_root():
    return {"message": "GapFinder AI Backend is running!"}

@app.post("/upload-material")
async def upload_material(
    file: UploadFile = File(...), 
    authorization: str = Header(None)
):
    user_email = get_user_email(authorization)
    
    db = SessionLocal()
    
    # 1. Create the Material record
    new_material = Material(
        user_email=user_email,
        file_name=file.filename
    )
    db.add(new_material)
    db.commit()
    db.refresh(new_material)
    
    # 2. Read file content
    file_content = await file.read()
    
    # 3. Process and Embed
    try:
        process_and_embed_pdf(file_content, new_material.id, db)
    except Exception as e:
        db.rollback()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
        
    db.close()
    return {"message": "File uploaded and processed successfully", "material_id": new_material.id}