import os
import time
import random
from typing import Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    update_paras_order_status,
    update_paras_payment_status,
    update_paras_artwork_featured,
    update_paras_service_price,
    update_paras_faq_answer,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing from environment variables."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# Keep this configurable through Render environment variables.
# If GEMINI_MODEL is not set, this is the default.
MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.8-flash"
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Paras Arts AI Agent",
    description=(
        "AI-powered business data analyst and "
        "data management agent for Paras Arts."
    ),
    version="2.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://paras-arts-ai-agent.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str
    session_id: str


# ============================================================
# PENDING CONFIRMATION ACTIONS
# ============================================================

# session_id -> pending action
#
# Example:
#
# {
#     "abc123": {
#         "tool_name": "update_paras_order_status",
#         "args": {
#             "order_id": "PA-123",
#             "new_status": "Completed"
#         }
#     }
# }
#
# NOTE:
# This is intentionally in-memory for now.
# It can later be moved to MongoDB/Redis for production
# multi-instance persistence.

pending_actions: Dict[str, Dict[str, Any]] = {}


# ============================================================
# WRITE TOOLS
# ============================================================

WRITE_TOOLS = {
    "update_paras_order_status",
    "update_paras_payment_status",
    "update_paras_artwork_featured",
    "update_paras_service_price",
    "update_paras_faq_answer",
}


# ============================================================
# AVAILABLE FUNCTIONS
# ============================================================

available_functions = {

    # --------------------------------------------------------
    # READ / ANALYSIS
    # --------------------------------------------------------

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

    "get_paras_business_summary": get_paras_business_summary,

    # --------------------------------------------------------
    # CONTROLLED WRITES
    # --------------------------------------------------------

    "update_paras_order_status": update_paras_order_status,
    "update_paras_payment_status": update_paras_payment_status,
    "update_paras_artwork_featured": update_paras_artwork_featured,
    "update_paras_service_price": update_paras_service_price,
    "update_paras_faq_answer": update_paras_faq_answer,
}


# ============================================================
# GEMINI FUNCTION DECLARATIONS
# ============================================================

function_declarations = [

    # ========================================================
    # ORDERS
    # ========================================================

    types.FunctionDeclaration(
        name="search_paras_orders",
        description=(
            "Search Paras Arts orders. "
            "Optionally filter by order status. "
            "Returns safe business fields only."
        ),
        parameters={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": (
                        "Optional order status. "
                        "Allowed values: Pending, Accepted, "
                        "In Progress, Completed, Cancelled."
                    ),
                }
            },
        },
    ),

    types.FunctionDeclaration(
        name="analyze_paras_orders",
        description=(
            "Analyze Paras Arts order statistics, "
            "including total orders and counts by status."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),

    types.FunctionDeclaration(
        name="analyze_paras_payments",
        description=(
            "Analyze Paras Arts payment statistics, "
            "including counts by payment status."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),

    types.FunctionDeclaration(
        name="analyze_paras_sketch_types",
        description=(
            "Analyze Paras Arts orders grouped by sketch type."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),

    types.FunctionDeclaration(
        name="analyze_paras_budgets",
        description=(
            "Analyze requested order budgets. "
            "Returns count, average, minimum, maximum "
            "and total requested budget. "
            "These values are NOT actual revenue."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),

    # ========================================================
    # ARTWORKS
    # ========================================================

    types.FunctionDeclaration(
        name="search_paras_artworks",
        description=(
            "Search Paras Arts artworks. "
            "Optionally filter by category or featured status."
        ),
        parameters={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional artwork category.",
                },
                "featured": {
                    "type": "boolean",
                    "description": "Optional featured filter.",
                },
            },
        },
    ),

    types.FunctionDeclaration(
        name="analyze_paras_artworks",
        description=(
            "Analyze Paras Arts artwork statistics, "
            "including total artworks, featured artworks "
            "and category counts."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),

    # ========================================================
    # SERVICES
    # ========================================================

    types.FunctionDeclaration(
        name="search_paras_services",
        description=(
            "Search Paras Arts services. "
            "Optionally search by service title."
        ),
        parameters={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": (
                        "Optional service title or title keyword."
                    ),
                }
            },
        },
    ),

    types.FunctionDeclaration(
        name="analyze_paras_services",
        description=(
            "Analyze Paras Arts services and their pricing information."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),

    # ========================================================
    # FAQS
    # ========================================================

    types.FunctionDeclaration(
        name="search_paras_faqs",
        description=(
            "Search Paras Arts FAQs. "
            "Optionally filter by category or keyword."
        ),
        parameters={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional FAQ category.",
                },
                "keyword": {
                    "type": "string",
                    "description": (
                        "Optional keyword to search "
                        "in FAQ questions and answers."
                    ),
                },
            },
        },
    ),

    types.FunctionDeclaration(
        name="analyze_paras_faqs",
        description=(
            "Analyze Paras Arts FAQ statistics "
            "and category counts."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),

    # ========================================================
    # BUSINESS SUMMARY
    # ========================================================

    types.FunctionDeclaration(
        name="get_paras_business_summary",
        description=(
            "Get a safe high-level summary of the Paras Arts "
            "business database. Includes counts for orders, "
            "artworks, services, FAQs, testimonials, messages "
            "and newsletter subscribers, plus order and payment "
            "statistics."
        ),
        parameters={
            "type": "object",
            "properties": {},
        },
    ),

    # ========================================================
    # CONTROLLED WRITE OPERATIONS
    # ========================================================

    types.FunctionDeclaration(
        name="update_paras_order_status",
        description=(
            "Update the status of a Paras Arts order. "
            "This is a WRITE operation. The backend must "
            "obtain explicit user confirmation before execution."
        ),
        parameters={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Paras Arts order ID.",
                },
                "new_status": {
                    "type": "string",
                    "description": (
                        "New order status. "
                        "Allowed values: Pending, Accepted, "
                        "In Progress, Completed, Cancelled."
                    ),
                },
            },
            "required": [
                "order_id",
                "new_status",
            ],
        },
    ),

    types.FunctionDeclaration(
        name="update_paras_payment_status",
        description=(
            "Update the payment status of a Paras Arts order. "
            "This is a WRITE operation. The backend must "
            "obtain explicit user confirmation before execution."
        ),
        parameters={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Paras Arts order ID.",
                },
                "new_payment_status": {
                    "type": "string",
                    "description": (
                        "New payment status. "
                        "Allowed values: Pending, Verified, Failed."
                    ),
                },
            },
            "required": [
                "order_id",
                "new_payment_status",
            ],
        },
    ),

    types.FunctionDeclaration(
        name="update_paras_artwork_featured",
        description=(
            "Change whether a Paras Arts artwork is featured. "
            "This is a WRITE operation. The backend must "
            "obtain explicit user confirmation before execution."
        ),
        parameters={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Artwork title.",
                },
                "featured": {
                    "type": "boolean",
                    "description": (
                        "Whether the artwork should be featured."
                    ),
                },
            },
            "required": [
                "title",
                "featured",
            ],
        },
    ),

    types.FunctionDeclaration(
        name="update_paras_service_price",
        description=(
            "Update the starting price of a Paras Arts service. "
            "This is a WRITE operation. The backend must "
            "obtain explicit user confirmation before execution."
        ),
        parameters={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Service title.",
                },
                "new_price": {
                    "type": "number",
                    "description": (
                        "New starting price in INR."
                    ),
                },
            },
            "required": [
                "title",
                "new_price",
            ],
        },
    ),

    types.FunctionDeclaration(
        name="update_paras_faq_answer",
        description=(
            "Update the answer of a Paras Arts FAQ. "
            "This is a WRITE operation. The backend must "
            "obtain explicit user confirmation before execution."
        ),
        parameters={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "FAQ question.",
                },
                "new_answer": {
                    "type": "string",
                    "description": "New FAQ answer.",
                },
            },
            "required": [
                "question",
                "new_answer",
            ],
        },
    ),
]


# ============================================================
# GEMINI TOOL CONFIG
# ============================================================

paras_tool = types.Tool(
    function_declarations=function_declarations
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are the Paras Arts AI Data Analyst and Data Management Agent.

Your job is to help the Paras Arts owner understand and manage
business data stored in MongoDB.

You have access ONLY to the controlled tools provided to you.

============================================================
READ OPERATIONS
============================================================

You can:

- Search orders
- Analyze order statistics
- Analyze payment statistics
- Analyze sketch types
- Analyze requested budgets
- Search artworks
- Analyze artworks
- Search services
- Analyze services
- Search FAQs
- Analyze FAQs
- Get a business summary

Always use the appropriate tool when the user asks about
actual Paras Arts database information.

Do NOT invent database values.

============================================================
CONTROLLED WRITE OPERATIONS
============================================================

You may request these controlled modifications:

- Update order status
- Update payment status
- Update artwork featured status
- Update service price
- Update FAQ answer

WRITE OPERATIONS MUST NEVER BE EXECUTED WITHOUT EXPLICIT
USER CONFIRMATION.

When the user asks to make a change, call the appropriate
write tool so that the backend can create a pending
confirmation action.

The backend will ask the user for confirmation.

Do not pretend that a write has happened before confirmation.

============================================================
DATABASE SECURITY
============================================================

NEVER:

- Access the admins collection
- Reveal admin passwords
- Reveal credentials
- Reveal customer phone numbers
- Reveal customer email addresses
- Reveal physical addresses
- Reveal reference image URLs
- Perform arbitrary MongoDB commands
- Delete database records
- Modify records using an unapproved operation
- Invent database information

Only use the provided tools.

============================================================
DATA INTERPRETATION
============================================================

Be accurate about the meaning of data.

Requested order budget is NOT revenue.

Payment status is NOT order status.

If there is not enough database information to answer a question,
say so clearly.

============================================================
RESPONSE STYLE
============================================================

Give concise, useful and well-formatted responses.

Prefer:

- Short headings
- Bullet points
- Small tables when useful
- Clear numbers
- Short explanations

Avoid unnecessarily long responses.

When reporting database results, distinguish between:

- Actual database facts
- Calculations based on database data
- General explanations

Never claim that a database modification happened until the
backend confirms that it was successfully executed.
"""


# ============================================================
# RETRY CONFIGURATION
# ============================================================

MAX_GEMINI_RETRIES = 3

RETRYABLE_ERROR_TEXT = (
    "503",
    "unavailable",
    "service unavailable",
    "temporarily unavailable",
    "overloaded",
    "429",
    "resource exhausted",
)


def is_retryable_gemini_error(error: Exception) -> bool:
    """
    Determine whether an exception appears to be a temporary
    Gemini availability or rate-limit problem.
    """

    error_text = str(error).lower()

    return any(
        marker.lower() in error_text
        for marker in RETRYABLE_ERROR_TEXT
    )


# ============================================================
# GEMINI CALL WITH RETRY / BACKOFF
# ============================================================

def generate_with_retry(contents):
    last_error = None

    for attempt in range(MAX_GEMINI_RETRIES + 1):

        try:
            return client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=[paras_tool],
                    automatic_function_calling=(
                        types.AutomaticFunctionCallingConfig(
                            disable=True
                        )
                    ),
                    temperature=0.2,
                    max_output_tokens=800,
                ),
            )

        except Exception as error:

            last_error = error

            if not is_retryable_gemini_error(error):
                raise

            if attempt >= MAX_GEMINI_RETRIES:
                raise

            delay = (
                (2 ** attempt)
                + random.uniform(0.2, 0.7)
            )

            print(
                f"[Gemini] Temporary error. "
                f"Retrying in {delay:.2f}s..."
            )

            time.sleep(delay)

    raise last_error


# ============================================================
# FUNCTION EXECUTION
# ============================================================

def execute_function(
    name: str,
    args: Dict[str, Any],
):
    function = available_functions.get(name)

    if not function:
        raise ValueError(
            f"Unknown function: {name}"
        )

    return function(**args)


# ============================================================
# CONFIRMATION MESSAGE
# ============================================================

def get_confirmation_message(
    tool_name: str,
    args: Dict[str, Any],
) -> str:

    if tool_name == "update_paras_order_status":

        return (
            "### ⚠️ Confirmation Required\n\n"
            f"Change order **{args.get('order_id')}** status "
            f"to **{args.get('new_status')}**?\n\n"
            "Reply **YES** to confirm or **NO** to cancel."
        )

    if tool_name == "update_paras_payment_status":

        return (
            "### ⚠️ Confirmation Required\n\n"
            f"Change payment status for order "
            f"**{args.get('order_id')}** to "
            f"**{args.get('new_payment_status')}**?\n\n"
            "Reply **YES** to confirm or **NO** to cancel."
        )

    if tool_name == "update_paras_artwork_featured":

        featured_text = (
            "featured"
            if args.get("featured")
            else "not featured"
        )

        return (
            "### ⚠️ Confirmation Required\n\n"
            f"Set artwork **{args.get('title')}** to "
            f"**{featured_text}**?\n\n"
            "Reply **YES** to confirm or **NO** to cancel."
        )

    if tool_name == "update_paras_service_price":

        return (
            "### ⚠️ Confirmation Required\n\n"
            f"Change service **{args.get('title')}** "
            f"starting price to "
            f"**₹{args.get('new_price')}**?\n\n"
            "Reply **YES** to confirm or **NO** to cancel."
        )

    if tool_name == "update_paras_faq_answer":

        return (
            "### ⚠️ Confirmation Required\n\n"
            "Update the answer for this FAQ?\n\n"
            f"> {args.get('question')}\n\n"
            "Reply **YES** to confirm or **NO** to cancel."
        )

    return (
        "### ⚠️ Confirmation Required\n\n"
        "A database modification has been requested.\n\n"
        "Reply **YES** to confirm or **NO** to cancel."
    )


# ============================================================
# HANDLE CONFIRMATION
# ============================================================

def handle_confirmation(
    message: str,
    session_id: str,
):

    normalized = message.strip().lower()

    pending = pending_actions.get(session_id)

    if not pending:
        return None

    # --------------------------------------------------------
    # CONFIRM
    # --------------------------------------------------------

    if normalized in {
        "yes",
        "y",
        "confirm",
        "confirmed",
    }:

        tool_name = pending["tool_name"]
        args = pending["args"]

        try:

            result = execute_function(
                tool_name,
                args,
            )

            pending_actions.pop(
                session_id,
                None,
            )

            return (
                "### ✅ Update Successful\n\n"
                f"{result}"
            )

        except Exception as error:

            pending_actions.pop(
                session_id,
                None,
            )

            print(
                f"[Write] Failed: "
                f"{type(error).__name__}: {error}"
            )

            return (
                "### ❌ Update Failed\n\n"
                "The database update could not be completed."
            )

    # --------------------------------------------------------
    # CANCEL
    # --------------------------------------------------------

    if normalized in {
        "no",
        "n",
        "cancel",
        "cancelled",
        "reject",
        "rejected",
    }:

        pending_actions.pop(
            session_id,
            None,
        )

        return (
            "### ❌ Update Cancelled\n\n"
            "No database changes were made."
        )

    # --------------------------------------------------------
    # INVALID CONFIRMATION
    # --------------------------------------------------------

    return (
        "A database update is waiting for confirmation.\n\n"
        "Please reply **YES** to confirm or **NO** to cancel."
    )


# ============================================================
# MAIN AGENT
# ============================================================

def run_agent(
    message: str,
    session_id: str,
):

    # --------------------------------------------------------
    # FIRST: CHECK PENDING CONFIRMATION
    # --------------------------------------------------------

    confirmation_result = handle_confirmation(
        message,
        session_id,
    )

    if confirmation_result is not None:
        return confirmation_result

    # --------------------------------------------------------
    # INITIAL USER MESSAGE
    # --------------------------------------------------------

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(
                    text=message
                )
            ],
        )
    ]

    # --------------------------------------------------------
    # TOOL LOOP
    # --------------------------------------------------------

    MAX_ITERATIONS = 4

    for _ in range(MAX_ITERATIONS):

        try:

            response = generate_with_retry(
                contents
            )

        except Exception as error:

            print(
                f"[Gemini] Request failed: "
                f"{type(error).__name__}: {error}"
            )

            if is_retryable_gemini_error(error):

                return (
                    "Gemini is temporarily unavailable right now. "
                    "Please try again in a few seconds."
                )

            return (
                "The AI agent encountered an error while "
                "processing your request."
            )

        # ----------------------------------------------------
        # NO FUNCTION CALL
        # ----------------------------------------------------

        if not response.function_calls:

            text = response.text

            if text:
                return text.strip()

            return (
                "I couldn't generate a response "
                "for that request."
            )

        # ----------------------------------------------------
        # APPEND MODEL RESPONSE
        # ----------------------------------------------------

        if response.candidates:

            candidate = response.candidates[0]

            if candidate.content:

                contents.append(
                    candidate.content
                )

        # ----------------------------------------------------
        # PROCESS FUNCTION CALLS
        # ----------------------------------------------------

        tool_responses = []

        for function_call in response.function_calls:

            tool_name = function_call.name

            args = dict(
                function_call.args or {}
            )

            print(
                f"[Agent] Function requested: "
                f"{tool_name} | args={args}"
            )

            # ------------------------------------------------
            # UNKNOWN TOOL
            # ------------------------------------------------

            if tool_name not in available_functions:

                tool_responses.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={
                            "error": "Unknown function."
                        },
                    )
                )

                continue

            # ------------------------------------------------
            # WRITE TOOL
            # ------------------------------------------------

            if tool_name in WRITE_TOOLS:

                pending_actions[session_id] = {
                    "tool_name": tool_name,
                    "args": args,
                }

                return get_confirmation_message(
                    tool_name,
                    args,
                )

            # ------------------------------------------------
            # READ TOOL
            # ------------------------------------------------

            try:

                result = execute_function(
                    tool_name,
                    args,
                )

                print(
                    f"[Tool] {tool_name} executed successfully."
                )

                # IMPORTANT:
                # Do NOT pass id= here.
                # Your installed SDK's
                # Part.from_function_response()
                # does not accept id as a keyword argument.

                tool_responses.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={
                            "result": result
                        },
                    )
                )

            except Exception as error:

                print(
                    f"[Tool] {tool_name} failed: "
                    f"{type(error).__name__}: {error}"
                )

                # IMPORTANT:
                # Same fix here: no id= argument.

                tool_responses.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={
                            "error": (
                                "The requested database "
                                "operation failed."
                            )
                        },
                    )
                )

        # ----------------------------------------------------
        # SEND TOOL RESULTS BACK TO GEMINI
        # ----------------------------------------------------

        if tool_responses:

            contents.append(
                types.Content(
                    role="user",
                    parts=tool_responses,
                )
            )

    # --------------------------------------------------------
    # MAX ITERATIONS
    # --------------------------------------------------------

    return (
        "I couldn't complete that request within the allowed "
        "number of tool operations. Please try a more specific request."
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "Paras Arts AI Agent",
        "mode": "business-data-management",
        "model": MODEL,
        "version": "2.1.0",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "Paras Arts AI Agent",
        "model": MODEL,
    }


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):

    message = request.message.strip()

    session_id = request.session_id.strip()

    if not message:

        return {
            "answer": "Please enter a message."
        }

    if not session_id:

        return {
            "answer": "Session ID is required."
        }

    try:

        answer = run_agent(
            message=message,
            session_id=session_id,
        )

        return {
            "answer": answer
        }

    except Exception as error:

        print(
            f"[API] Unexpected error: "
            f"{type(error).__name__}: {error}"
        )

        return {
            "answer": (
                "The Paras Arts AI Agent encountered "
                "an unexpected error."
            )
        }


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(
            os.getenv(
                "PORT",
                "8000"
            )
        ),
        reload=False,
    )