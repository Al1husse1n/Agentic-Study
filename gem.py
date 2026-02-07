from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from tools import *
import json

load_dotenv()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
client=genai.Client(api_key=GEMINI_API_KEY)

#Map name with the function
tools_map={
    "summarize_text":summarize_text,
    "generate_questions":generate_questions,
    "extract_questions":extract_questions
}

#function declarations
function_declaration=[
    types.FunctionDeclaration(
        name="summarize_text",
        description="create summary of the chapter content",
        parameters={
            "type":"object",
            "properties":{
                "file_path":{"type":"string"}
            },
            "required":["file_path"]
        }
    ),
    types.FunctionDeclaration(
        name="generate_questions",
        description="generate high-quality questions from textbook chapter",
        parameters={
            "type":"object",
            "properties":{
                "file_path":{"type":"string"}
            },
            "required":["file_path"]
        }
    ),
    types.FunctionDeclaration(
        name="extract_questions",
        description="extract ONLY the questions that belong to the specific chapter provided from the questions provided.",
        parameters={
            "type":"object",
            "properties":{
                "chapter_file":{"type":"string"},
                "questions_file":{"type":"string"}
            },
            "required":["chapter_file","questions_file"]
        }
    )
]

#Tool object
tool = types.Tool(function_declarations=function_declaration)

user_prompt=input("What do you want to do: ")

#Agent loop
history= [
    types.Content(
        role="user",
        parts=[
            types.Part.from_text(text=user_prompt)
        ]
    )
]

system_message = """
You are an expert study assistant helping a student prepare for an upcoming exam.
The student is in a hurry and wants focused, efficient help.

Rules:
- You only assist with studying-related requests.
- If a request does not require a tool, answer directly.
- Answer only using well-known facts or clearly state when you are unsure.
- Do not invent information or assume missing details.
- If a tool is required but one or more arguments are missing, ask the student to provide them.
- Do not fill in missing tool arguments yourself.
- Call at most one tool per turn.
"""

system_inst = types.Content(
    parts=[types.Part.from_text(text=system_message)]
)

while True:
    response= client.models.generate_content(
        model="gemini-2.5-flash",
        contents=history,
        config=types.GenerateContentConfig(
            system_instruction=system_inst,
            tools=[tool]
        )
    )

    candidate = response.candidates[0]
    content = candidate.content
    history.append(content)

    function_calls = [
        part.function_call
        for part in content.parts
        if part.function_call is not None
    ]

    if not function_calls:
        print("\nFinal Answer:\n")
        final_text = "".join(
        part.text for part in content.parts if part.text
        )
        print(final_text)
        break

    for fc in function_calls:
        func_name = fc.name
        args = dict(fc.args)

        print(f"\nCalling tool: {func_name}")
        print("Arguments:", args)

        try:
            if func_name not in tools_map:
                raise RuntimeError(f"Unknown tool requested: {func_name}")
            result = tools_map[func_name](**args)
            result_str = json.dumps({"result": result})  # usually JSON string
        except Exception as e:
            result_str = json.dumps({"error": str(e)})

        print("Tool result:", result_str)

        # Append function response to history
        history.append(
            types.Content(
                role="tool",
                parts=[
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=func_name,
                            response={"result": result}  
                        )
                    )
                ]
            )

        )

