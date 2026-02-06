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
        return{"extraction_error": str(e)}
    

print(summarize_text("DataStructureCH1.pdf"))
