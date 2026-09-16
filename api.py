
import os

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel

from google import genai

from google.genai import types

from paras_tools import (
    search_paras_orders,
    analyze_paras_orders,
    analyze_paras_payments,
    analyze_paras_sketch_types,
    analyze_paras_budgets,
    search_paras_artworks,
    analyze_paras_artworks,
    search_paras_services,
    analyze_paras_services,
    search_paras_faqs,
    analyze_paras_faqs,
    get_paras_business_summary,
)


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing.")


client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-3.6-flash"


app = FastAPI(
    title="Paras Arts AI Data Agent",
    description="AI agent for analyzing Paras Arts MongoDB data.",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


tools = types.Tool(
    function_declarations=[
        {
            "name": "search_paras_orders",
            "description": "Search Paras Arts orders using filters such as status, payment status, sketch type, paper size, or budget.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "status": {
                        "type": "STRING",
                        "description": "Order status."
                    },
                    "payment_status": {
                        "type": "STRING",
                        "description": "Payment status."
                    },
                    "sketch_type": {
                        "type": "STRING",
                        "description": "Sketch/service type."
                    },
                    "paper_size": {
                        "type": "STRING",
                        "description": "Paper size such as A4, A3, A2."
                    },
                    "min_budget": {
                        "type": "NUMBER",
                        "description": "Minimum requested budget."
                    },
                    "max_budget": {
                        "type": "NUMBER",
                        "description": "Maximum requested budget."
                    },
                },
            },
        },
        {
            "name": "analyze_paras_orders",
            "description": "Analyze Paras Arts order statistics.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
            },
        },
        {
            "name": "analyze_paras_payments",
            "description": "Analyze Paras Arts payment status statistics.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
            },
        },
        {
            "name": "analyze_paras_sketch_types",
            "description": "Analyze order counts by sketch type.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
            },
        },
        {
            "name": "analyze_paras_budgets",
            "description": "Analyze requested order budgets including average, minimum, maximum and total requested budget.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
            },
        },
        {
            "name": "search_paras_artworks",
            "description": "Search Paras Arts artworks by category, title or featured status.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "category": {
                        "type": "STRING",
                        "description": "Artwork category."
                    },
                    "title": {
                        "type": "STRING",
                        "description": "Artwork title."
                    },
                    "featured": {
                        "type": "BOOLEAN",
                        "description": "Whether artwork is featured."
                    },
                },
            },
        },
        {
            "name": "analyze_paras_artworks",
            "description": "Analyze Paras Arts artwork statistics.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
            },
        },
        {
            "name": "search_paras_services",
            "description": "Search Paras Arts services.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "title": {
                        "type": "STRING",
                        "description": "Service title."
                    },
                },
            },
        },
        {
            "name": "analyze_paras_services",
            "description": "Analyze Paras Arts service statistics.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
            },
        },
        {
            "name": "search_paras_faqs",
            "description": "Search Paras Arts FAQs.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "category": {
                        "type": "STRING",
                        "description": "FAQ category."
                    },
                    "keyword": {
                        "type": "STRING",
                        "description": "Keyword to search inside FAQ questions and answers."
                    },
                },
            },
        },
        {
            "name": "analyze_paras_faqs",
            "description": "Analyze Paras Arts FAQ statistics.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
            },
        },
        {
            "name": "paras_business_summary",
            "description": "Return an overall Paras Arts business data summary.",
            "parameters": {
                "type": "OBJECT",
                "properties": {},
            },
        },
    ]
)


available_functions = {
    "search_paras_orders": search_paras_orders,
    "analyze_paras_orders": analyze_paras_orders,
    "analyze_paras_payments": analyze_paras_payments,
    "analyze_paras_sketch_types": analyze_paras_sketch_types,
    "analyze_paras_budgets": analyze_paras_budgets,
    "search_paras_artworks": search_paras_artworks,
    "analyze_paras_artworks": analyze_paras_artworks,
    "search_paras_services": search_paras_services,
    "analyze_paras_services": analyze_paras_services,
    "search_paras_faqs": search_paras_faqs,
    "analyze_paras_faqs": analyze_paras_faqs,
    "paras_business_summary": get_paras_business_summary,
}


SYSTEM_INSTRUCTION = """
You are the Paras Arts AI Data Agent.

You help analyze data from the Paras Arts MongoDB database.

You can:

- Search orders
- Analyze orders
- Analyze payment statuses
- Analyze sketch types
- Analyze requested budgets
- Search artworks
- Analyze artworks
- Search services
- Analyze services
- Search FAQs
- Analyze FAQs
- Provide business summaries

Important rules:

1. Never access or expose the admins collection.

2. Never expose sensitive customer information such as:
   - phone numbers
   - email addresses
   - physical addresses
   - reference image URLs
   - private image URLs

3. Requested order budgets are NOT confirmed revenue.

4. Do not invent database information.

5. Use tools when database information is required.

6. Explain results clearly and simply.

7. This deployed version is READ-ONLY.

8. Do not attempt database write operations.
"""


def execute_function(function_name, args):
    if function_name not in available_functions:
        raise ValueError(f"Unknown function: {function_name}")

    function = available_functions[function_name]

    if args is None:
        args = {}

    return function(**args)


def is_quota_error(error):
    """
    Detect Gemini quota/rate-limit errors.
    """
    error_text = str(error).upper()

    return (
        "429" in error_text
        or "RESOURCE_EXHAUSTED" in error_text
        or "QUOTA" in error_text
        or "RATE LIMIT" in error_text
    )


def run_agent(user_message):

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[tools],
            ),
        )

    except Exception as e:
        print(f"Gemini error: {e}")

        if is_quota_error(e):
            return (
                "The AI service is temporarily unavailable because "
                "the Gemini API quota has been reached. Please try again later."
            )

        return (
            "The AI service is temporarily unavailable. "
            "Please try again later."
        )


    while response.function_calls:

        function_responses = []

        for function_call in response.function_calls:

            function_name = function_call.name

            function_args = dict(function_call.args or {})

            print(
                f"[TOOL] {function_name} "
                f"{function_args}"
            )

            try:
                result = execute_function(
                    function_name,
                    function_args
                )

            except Exception as e:
                print(f"Tool error: {e}")

                return (
                    "I couldn't retrieve the requested data right now. "
                    "Please try again later."
                )

            function_responses.append(
                types.Part.from_function_response(
                    name=function_name,
                    response={
                        "result": result
                    },
                )
            )


        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=[
                    user_message,
                    response.candidates[0].content,
                    *function_responses,
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    tools=[tools],
                ),
            )

        except Exception as e:
            print(f"Gemini follow-up error: {e}")

            if is_quota_error(e):
                return (
                    "The AI service is temporarily unavailable because "
                    "the Gemini API quota has been reached. Please try again later."
                )

            return (
                "The AI service is temporarily unavailable. "
                "Please try again later."
            )


    return response.text


@app.get("/")
def root():

    return {
        "status": "online",
        "service": "Paras Arts AI Data Agent",
        "version": "1.0.0",
        "database": "test",
        "mode": "read-only",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:

        answer = run_agent(request.message)

        return ChatResponse(
            answer=answer
        )

    except Exception as e:

        print(f"Agent error: {e}")

        raise HTTPException(
            status_code=500,
            detail="The AI service is temporarily unavailable. Please try again later."
        )