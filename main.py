from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from gem import *

app = FastAPI()



class AgentParameters(BaseModel):
    prompt:str = Field(...,description="Your prompt")
    chapter_file:Optional[UploadFile] = Field(None, description="The chapter file")
    questions_file:Optional[UploadFile] = Field(None, description="The questions file")

async def upload_fastapi_file_to_gemini(file:UploadFile):
    suffix = f".{file.filename.split('.')[-1]}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        temp_path = tmp.name

    uploaded_file = client.files.upload(
        file=temp_path,
        config={
            "display_name": file.filename,  
            "mime_type": file.content_type  
        }
    )
    os.remove(temp_path)  # clean up temp file
    return uploaded_file.name  # Gemini’s internal file ID, NOT the original filename, used to search up the file in gemini database


@app.post("/response")
async def agent_response(
    prompt: str = Form(),  # Get from form
    chapter_file: Optional[UploadFile] = File(None),  # Get file 1
    questions_file: Optional[UploadFile] = File(None)  # Get file 2
):
    if chapter_file:
        chapter_file = await upload_fastapi_file_to_gemini(chapter_file)
    if questions_file:
        questions_file = await upload_fastapi_file_to_gemini(questions_file)  
    return study_agent(prompt, chapter_file, questions_file)

