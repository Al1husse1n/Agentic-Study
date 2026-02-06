from google import genai
import os
from typing import IO, BinaryIO, TextIO
import magic  # pip install python-magic
import fitz   # pip install pymupdf   (for PDF)
from docx import Document  # pip install python-docx   (for DOCX)
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
client=genai.Client(api_key=GEMINI_API_KEY)

def extract_text(file_path: str) -> dict:
    if not os.path.isfile(file_path):
        return {"extraction_error": "File not found"}
    try:
        mime = magic.Magic(mime=True).from_file(file_path)
    except Exception as e:
        return {"extraction_error": f"Magic detection failed: {str(e)}"}

    content = ""

    try:
        if mime == "application/pdf":
            doc = fitz.open(file_path)
            pages = [page.get_text("text") for page in doc]
            content = "\n\n".join(pages)
            doc.close()

        elif mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(file_path)
            content = "\n".join(para.text for para in doc.paragraphs if para.text.strip())

        elif mime.startswith("text/") or mime in ("application/octet-stream",):
            # Treat as plain text if it starts with text/ or fallback
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()

        else:
            return {"extraction_error": f"Unsupported MIME type: {mime}"}

        content = content.strip()

        if not content:
            return {"extraction_error": "No text extracted"}
        return content  
    except Exception as e:
        return {"extraction_error": f"Extraction failed: {str(e)}"}
    
def summarize_text(file_path:str):
    try:
        content=extract_text(file_path)
        if type(content)==dict:
            return content
    except Exception as e:
        return str(e)
    
    prompt=f"""
You are an expert academic summarizer.

Task:
Create a clear, concise, and accurate summary of the following chapter content.

Guidelines:
- Aim for 200–400 words (about 15–25% of original length)
- Capture the main thesis / central argument
- Include the most important supporting points, key examples, and conclusions
- Preserve the logical flow and structure of the chapter
- Use neutral, objective language
- Avoid unnecessary details, minor examples, repetitive statements
- Do NOT add your own opinions or external information
- Do NOT include direct quotes unless they are absolutely essential

Structure the summary like this:
1. Opening sentence: main purpose / thesis of the chapter
2. Key arguments / sections (in order)
3. Important evidence or examples (briefly)
4. Closing: main takeaway / conclusion

Chapter content:
{content}
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )

        return {"extracted text":response.candidates[0].content.parts[0].text}
    except Exception as e:
        return{"summary error": str(e)}
    

def generate_questions(file_path:str):
    try:
        content=extract_text(file_path)
        if type(content)==dict:
            return content
    except Exception as e:
        return str(e)
    prompt = f"""
You are an expert educational content creator specializing in generating high-quality questions from textbook chapters.

Task:
Generate a set of questions based on the following chapter content.

Guidelines:
- Create 10–15 questions total
- Use a balanced mix of question types:
  - 3–4 factual/recall questions (who, what, when, where)
  - 3–4 comprehension/understanding questions (explain, describe, how)
  - 2–3 analytical/inferential questions (why, implications, relationships)
  - 2–3 application or critical thinking questions (evaluate, compare, predict, real-world connection)
  - 1–2 open-ended/discussion questions
- Questions should cover the main ideas, key details, important concepts, and conclusions
- Make questions clear, precise, and unambiguous
- Vary difficulty from easy to more challenging
- Do NOT provide answers — only the questions
- Number the questions
- Group them by type if possible (e.g. Recall Questions, Understanding Questions, etc.)

Chapter content:
{content}
"""    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        return {"Generated questions":response.candidates[0].content.parts[0].text}
    except Exception as e:
        return{"generate_question_error":str(e)}

def extract_questions(chapter_file:str, questions_file:str):
    try:
        chapter = extract_text(chapter_file)
        questions = extract_text(questions_file)
        if type(chapter) == dict:
            return chapter
        elif type(questions) == dict:
            return questions
    except Exception as e:
        return str(e)
        
    prompt = f"""
You are an extraction assistant.

Your task is to extract ONLY the questions that belong to a specific chapter.

You will be given:
- A text from the chapter
- A text from the questions

Rules:
- Return ONLY questions related to the given chapter.
- Do NOT rewrite or summarize questions.
- Do NOT include questions from other chapters.
- If no questions belong to the chapter, return that you couldn't find anything.
- Include the question number of the question, if available
- the question may be a choose question so include the choices as well

The text from the chapter:{chapter}
The text from the question:{questions}
"""
    try:
        response= client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        return {"Extracted questions": response.candidates[0].content.parts[0].text}
    
    except Exception as e:
        return{"extract_question_error": str(e)}
    
print(extract_questions("Subnetting.pdf","NetworksQuestions.pdf"))