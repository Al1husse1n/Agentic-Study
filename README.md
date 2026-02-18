# 📚 AI Study Assistant – Gemini + FastAPI

An intelligent backend service that helps students study smarter — not harder.

Upload chapters or past exams → get summaries, high-quality questions, filtered chapter-specific questions, and focused concept explanations — all powered by Google Gemini.

Built with **agentic reasoning** (planner → tool → observe → decide → repeat) so the system thinks before it answers.

---

## ✨ What it can do

| Feature                              | Description                                                                 |
|:-------------------------------------|:----------------------------------------------------------------------------|
| Chapter Summarization                | Turns long PDFs/DOCX into concise, structured academic summaries            |
| Exam-Style Question Generation       | Creates balanced questions (recall, comprehension, application, analysis)  |
| Chapter-Specific Question Extraction | Filters a big question bank → only keeps questions relevant to one chapter |
| Past Exam Concept Analysis           | Identifies high-yield concepts likely to reappear + suggests focus areas    |

---

## 🧠 How the agent thinks

The system is **not** a simple prompt → response wrapper.

It uses a **multi-step reasoning loop** with:

- Planner decides what needs to be done  
- Tool selector picks the right tool(s)  
- Tool executor runs them safely (with argument validation)  
- Observation integrates results  
- Loop continues until the goal is clearly achieved  
- Explicit stopping condition prevents infinite loops

**Available tools** (the agent chooses which to call):

- `summarize_text`  
- `generate_questions`  
- `extract_questions`  
- `conceptualize_questions`

---

## 🏗 Architecture at a glance

User request
     ↓
FastAPI endpoint (/response)
     ↓
Upload → Gemini File API (persistent storage)
     ↓
Agent Loop
   ├─ Planner → reasons about the task
   ├─ Tool selection & argument validation
   ├─ Tool execution (Gemini function calling)
   ├─ Observation → adds result to context
   └─ Repeat until done
     ↓
Structured JSON response


---

## 🛠 Tech Stack

| Layer              | Technology                          |
|--------------------|-------------------------------------|
| Backend            | FastAPI                             |
| AI / LLM           | Google Gemini 1.5 Flash / 2.5 Flash |
| Agent framework    | Custom reasoning loop + function calling |
| File handling      | Gemini File API                     |
| Environment        | python-dotenv                       |
| ASGI server        | Uvicorn                             |

---

## 🚀 Quick Start

```bash
# 1. Clone & enter directory
git clone https://github.com/YOUR_USERNAME/ai-study-assistant.git
cd ai-study-assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env
# → edit .env and add your GEMINI_API_KEY

# 5. Run the server
uvicorn main:app --reload

# API Endpoints – AI Study Assistant

All endpoints are served under the FastAPI application.

Base URL (local development):  
`http://127.0.0.1:8000`

Interactive documentation (Swagger UI):  
`http://127.0.0.1:8000/docs`  
(ReDoc alternative: `/redoc`)

## Main Endpoint

### `POST /response`

**Description**  
The primary endpoint that accepts a user prompt and optional files.  
The agentic system processes the request using reasoning, tool selection, and Google Gemini.

**Content-Type**: `multipart/form-data`

**Form fields** (all sent as form data):

| Field            | Type     | Required | Description                                                                 |
|------------------|----------|----------|-----------------------------------------------------------------------------|
| `prompt`         | string   | **Yes**  | The user's instruction or question (e.g. "Summarize this chapter", "Generate 20 questions") |
| `chapter_file`   | file     | Optional | PDF or DOCX file containing the chapter content                             |
| `questions_file` | file     | Optional | PDF or DOCX file containing past exam questions or question bank            |

**Supported file types**  
- PDF  
- DOCX  

**Example requests** (using curl or Postman)

```bash
# 1. Summarize a chapter
curl -X POST "http://127.0.0.1:8000/response" \
  -F "prompt=Summarize this chapter in detail" \
  -F "chapter_file=@path/to/chapter3.pdf"


Example prompts"Summarize this chapter"
"Generate 20 high-quality exam questions"
"Extract only questions related to Chapter 3"
"Analyze this past exam and tell me the most important concepts to revise"

Response → clean JSON with answer, reasoning_steps (optional), sources etc.

 Environment Variables (.env)

GEMINI_API_KEY=your_api_key_here
# Optional - for debugging / logging
LOG_LEVEL=INFO

 AuthorAli Hussein
GitHub: @Al1husse1n
Email: alihusseinali284@gmail.com


