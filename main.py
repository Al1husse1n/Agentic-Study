from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from gem import *

app = FastAPI()

class AgentResponse(BaseModel):
    text:str
    tools:list

    class Config:
        from_attribute=True

class AgentParameters(BaseModel):
    prompt:str = Field(...,description="Your prompt")
    chapter_file:Optional[str] = Field(None, description="path of the chapter file")
    question_file:Optional[str] = Field(None, description="path of the questions file")

@app.post("/response")
def agent_response(user_input:AgentParameters):
    chapter_file = "" if user_input.chapter_file is None else f" chapter file: {user_input.chapter_file}"
    question_file = "" if user_input.question_file is None else f" Questions file: {user_input.question_file}"
    prompt = user_input.prompt + chapter_file + question_file
    return study_agent(prompt)

