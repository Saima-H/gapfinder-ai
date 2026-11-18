from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from pgvector.sqlalchemy import Vector

# 1. The uploaded study materials (PDFs/Notes)
class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False, index=True)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    topics = relationship("Topic", back_populates="material")
    chunks = relationship("DocumentChunk", back_populates="material")

# 2. The topics extracted from the syllabus
class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(String, default="Not Tested") # Weak, Medium, Strong
    
    material = relationship("Material", back_populates="topics")

# 3. The RAG Chunks (Vector Embeddings)
# Note: OpenAI's text-embedding-3-small outputs exactly 1536 dimensions
class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536)) # The pgvector column for AI search
    
    material = relationship("Material", back_populates="chunks")

# 4. The Diagnostic Quizzes
class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    score = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())

# 5. The individual questions generated
class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    citation = Column(String, nullable=False) # e.g., "Chapter 3, Section 2"