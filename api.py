import os
import uuid
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

from paras_tools import (
    db,

    # READ TOOLS
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

    # WRITE TOOLS
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
    raise RuntimeError("GEMINI_API_KEY is not configured.")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-3.6-flash"


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Paras Arts AI Data Agent",
    description="AI agent for analyzing and managing Paras Arts business data.",
    version="2.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://paras-arts-ai-agent.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    answer: str


# ============================================================
# PENDING WEB CONFIRMATIONS
# ============================================================
#
# Example:
#
# User:
#   Change order PA-1001 to Completed
#
# Agent:
#   Confirmation required...
#
# Backend stores:
# {
#   "session-id": {
#       "function_name": "update_paras_order_status",
#       "args": {
#           "order_id": "PA-1001",
#           "new_status": "Completed"
#       }
#   }
# }
#
# User:
#   YES
#
# Backend executes the stored function.
#
# This is intentionally kept in memory for this project/demo.
# ============================================================

pending_actions: Dict[str, Dict[str, Any]] = {}


# ============================================================
# WRITE TOOL NAMES
# ============================================================

WRITE_TOOLS = {
    "update_paras_order_status",
    "update_paras_payment_status",
    "update_paras_artwork_featured",
    "update_paras_service_price",
    "update_paras_faq_answer",
}


# ============================================================
# GEMINI TOOL DECLARATIONS
# ============================================================

tools = [
    types.Tool(
        function_declarations=[
            # ------------------------------------------------
            # ORDERS
            # ------------------------------------------------

            types.FunctionDeclaration(
                name="search_paras_orders",
                description=(
                    "Search Paras Arts orders. "
                    "Can filter by order status."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "status": types.Schema(
                            type="STRING",
                            description=(
                                "Optional order status such as "
                                "Pending, Accepted, In Progress, "
                                "Completed, or Cancelled."
                            ),
                        )
                    },
                    required=[],
                ),
            ),

            types.FunctionDeclaration(
                name="analyze_paras_orders",
                description=(
                    "Analyze Paras Arts order data and provide "
                    "counts, trends, and useful statistics."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                    required=[],
                ),
            ),

            types.FunctionDeclaration(
                name="analyze_paras_payments",
                description=(
                    "Analyze payment statuses for Paras Arts orders."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                    required=[],
                ),
            ),

            types.FunctionDeclaration(
                name="analyze_paras_sketch_types",
                description=(
                    "Analyze the different sketch types in Paras Arts orders."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                    required=[],
                ),
            ),

            types.FunctionDeclaration(
                name="analyze_paras_budgets",
                description=(
                    "Analyze requested customer budgets in Paras Arts orders. "
                    "Requested budgets are not the same as actual revenue."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                    required=[],
                ),
            ),

            # ------------------------------------------------
            # ARTWORKS
            # ------------------------------------------------

            types.FunctionDeclaration(
                name="search_paras_artworks",
                description=(
                    "Search Paras Arts artwork records."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "category": types.Schema(
                            type="STRING",
                            description="Optional artwork category.",
                        )
                    },
                    required=[],
                ),
            ),

            types.FunctionDeclaration(
                name="analyze_paras_artworks",
                description=(
                    "Analyze Paras Arts artwork data."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                    required=[],
                ),
            ),

            # ------------------------------------------------
            # SERVICES
            # ------------------------------------------------

            types.FunctionDeclaration(
                name="search_paras_services",
                description=(
                    "Search Paras Arts service records."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                    required=[],
                ),
            ),

            types.FunctionDeclaration(
                name="analyze_paras_services",
                description=(
                    "Analyze Paras Arts services."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                    required=[],
                ),
            ),

            # ------------------------------------------------
            # FAQS
            # ------------------------------------------------

            types.FunctionDeclaration(
                name="search_paras_faqs",
                description=(
                    "Search Paras Arts FAQ records."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                    required=[],
                ),
            ),

            types.FunctionDeclaration(
                name="analyze_paras_faqs",
                description=(
                    "Analyze Paras Arts FAQ data."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                    required=[],
                ),
            ),

            # ------------------------------------------------
            # BUSINESS SUMMARY
            # ------------------------------------------------

            types.FunctionDeclaration(
                name="get_paras_business_summary",
                description=(
                    "Get a complete summary of Paras Arts business data."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={},
                    required=[],
                ),
            ),

            # =================================================
            # WRITE OPERATIONS
            # =================================================

            types.FunctionDeclaration(
                name="update_paras_order_status",
                description=(
                    "Update the status of a Paras Arts order. "
                    "Allowed statuses are Pending, Accepted, "
                    "In Progress, Completed, and Cancelled. "
                    "The application requires explicit confirmation "
                    "before executing this operation."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "order_id": types.Schema(
                            type="STRING",
                            description="The exact Paras Arts order ID.",
                        ),
                        "new_status": types.Schema(
                            type="STRING",
                            description=(
                                "New order status: Pending, Accepted, "
                                "In Progress, Completed, or Cancelled."
                            ),
                        ),
                    },
                    required=["order_id", "new_status"],
                ),
            ),

            types.FunctionDeclaration(
                name="update_paras_payment_status",
                description=(
                    "Update the payment status of a Paras Arts order. "
                    "Allowed statuses are Pending, Verified, and Failed. "
                    "The application requires explicit confirmation "
                    "before executing this operation."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "order_id": types.Schema(
                            type="STRING",
                            description="The exact Paras Arts order ID.",
                        ),
                        "new_payment_status": types.Schema(
                            type="STRING",
                            description=(
                                "New payment status: Pending, Verified, "
                                "or Failed."
                            ),
                        ),
                    },
                    required=["order_id", "new_payment_status"],
                ),
            ),

            types.FunctionDeclaration(
                name="update_paras_artwork_featured",
                description=(
                    "Change whether a Paras Arts artwork is featured. "
                    "The application requires explicit confirmation "
                    "before executing this operation."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "title": types.Schema(
                            type="STRING",
                            description="Exact artwork title.",
                        ),
                        "featured": types.Schema(
                            type="BOOLEAN",
                            description=(
                                "True to feature the artwork, "
                                "false to remove it from featured."
                            ),
                        ),
                    },
                    required=["title", "featured"],
                ),
            ),

            types.FunctionDeclaration(
                name="update_paras_service_price",
                description=(
                    "Update the price of a Paras Arts service. "
                    "The application requires explicit confirmation "
                    "before executing this operation."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "title": types.Schema(
                            type="STRING",
                            description="Exact service title.",
                        ),
                        "new_price": types.Schema(
                            type="NUMBER",
                            description="New service price.",
                        ),
                    },
                    required=["title", "new_price"],
                ),
            ),

            types.FunctionDeclaration(
                name="update_paras_faq_answer",
                description=(
                    "Update the answer of an existing Paras Arts FAQ. "
                    "The application requires explicit confirmation "
                    "before executing this operation."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "question": types.Schema(
                            type="STRING",
                            description="Exact FAQ question.",
                        ),
                        "new_answer": types.Schema(
                            type="STRING",
                            description="New FAQ answer.",
                        ),
                    },
                    required=["question", "new_answer"],
                ),
            ),
        ]
    )
]


# ============================================================
# AVAILABLE FUNCTIONS
# ============================================================

available_functions = {
    # READ
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

    # WRITE
    "update_paras_order_status": update_paras_order_status,
    "update_paras_payment_status": update_paras_payment_status,
    "update_paras_artwork_featured": update_paras_artwork_featured,
    "update_paras_service_price": update_paras_service_price,
    "update_paras_faq_answer": update_paras_faq_answer,
}


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are the Paras Arts AI Data Agent.

You are connected to the Paras Arts MongoDB business database.

Your job is to help the owner understand and manage business data.

You can:
- search orders
- analyze orders
- analyze payments
- analyze sketch types
- analyze requested budgets
- search and analyze artworks
- search and analyze services
- search and analyze FAQs
- provide business summaries
- perform a small set of controlled database updates

IMPORTANT DATA RULES:

1. NEVER access or discuss the admins collection.
2. NEVER expose passwords, authentication credentials, tokens, API keys,
   private reference-image URLs, physical addresses, phone numbers, or
   other sensitive customer contact information.
3. Requested customer budgets are NOT actual revenue.
4. Do not invent revenue, profit, or financial information.
5. Do not perform delete operations.
6. Do not execute arbitrary MongoDB commands.
7. Do not create arbitrary database queries.
8. Only use the provided tools.
9. For updates, only use the specific update tools provided.
10. Never claim that a database update succeeded unless the tool actually
    returned a successful result.

CONTROLLED WRITE OPERATIONS:

The application supports these controlled updates:

- update order status
- update payment status
- update artwork featured status
- update service price
- update FAQ answer

A database write must NEVER be treated as automatically authorized.

The application itself handles confirmation before executing writes.

When a user requests a write operation, call the appropriate write tool
with the requested values. The application will intercept the operation
and ask the user for confirmation before execution.

Keep responses clear and concise.

When presenting customer orders, avoid exposing sensitive contact details.
Use order IDs and non-sensitive business information where possible.
"""


# ============================================================
# CONFIRMATION HELPERS
# ============================================================

def get_confirmation_message(function_name: str, args: Dict[str, Any]) -> str:
    """
    Create a safe human-readable confirmation message.
    """

    if function_name == "update_paras_order_status":
        order_id = args.get("order_id")
        new_status = args.get("new_status")

        order = db["orders"].find_one(
            {"orderId": order_id},
            {
                "orderId": 1,
                "status": 1,
                "sketchType": 1,
            },
        )

        if not order:
            return (
                f"❌ I couldn't find order `{order_id}`. "
                "No database change was made."
            )

        current_status = order.get("status", "Unknown")
        sketch_type = order.get("sketchType", "Unknown")

        return (
            "⚠️ **Database update requires confirmation**\n\n"
            f"**Order:** {order_id}\n"
            f"**Sketch type:** {sketch_type}\n"
            f"**Current status:** {current_status}\n"
            f"**New status:** {new_status}\n\n"
            "Type **YES** to confirm this update or **NO** to cancel."
        )

    if function_name == "update_paras_payment_status":
        order_id = args.get("order_id")
        new_status = args.get("new_payment_status")

        order = db["orders"].find_one(
            {"orderId": order_id},
            {
                "orderId": 1,
                "paymentStatus": 1,
            },
        )

        if not order:
            return (
                f"❌ I couldn't find order `{order_id}`. "
                "No database change was made."
            )

        current_status = order.get("paymentStatus", "Unknown")

        return (
            "⚠️ **Database update requires confirmation**\n\n"
            f"**Order:** {order_id}\n"
            f"**Current payment status:** {current_status}\n"
            f"**New payment status:** {new_status}\n\n"
            "Type **YES** to confirm this update or **NO** to cancel."
        )

    if function_name == "update_paras_artwork_featured":
        title = args.get("title")
        new_featured = args.get("featured")

        artwork = db["artworks"].find_one(
            {"title": title},
            {
                "title": 1,
                "featured": 1,
            },
        )

        if not artwork:
            return (
                f"❌ I couldn't find artwork `{title}`. "
                "No database change was made."
            )

        current_featured = artwork.get("featured", False)

        return (
            "⚠️ **Database update requires confirmation**\n\n"
            f"**Artwork:** {title}\n"
            f"**Currently featured:** {current_featured}\n"
            f"**New featured value:** {new_featured}\n\n"
            "Type **YES** to confirm this update or **NO** to cancel."
        )

    if function_name == "update_paras_service_price":
        title = args.get("title")
        new_price = args.get("new_price")

        service = db["services"].find_one(
            {"title": title},
            {
                "title": 1,
                "price": 1,
            },
        )

        if not service:
            return (
                f"❌ I couldn't find service `{title}`. "
                "No database change was made."
            )

        current_price = service.get("price", "Unknown")

        return (
            "⚠️ **Database update requires confirmation**\n\n"
            f"**Service:** {title}\n"
            f"**Current price:** ₹{current_price}\n"
            f"**New price:** ₹{new_price}\n\n"
            "Type **YES** to confirm this update or **NO** to cancel."
        )

    if function_name == "update_paras_faq_answer":
        question = args.get("question")
        new_answer = args.get("new_answer")

        faq = db["faqs"].find_one(
            {"question": question},
            {
                "question": 1,
                "answer": 1,
            },
        )

        if not faq:
            return (
                "❌ I couldn't find that FAQ question. "
                "No database change was made."
            )

        current_answer = faq.get("answer", "")

        return (
            "⚠️ **Database update requires confirmation**\n\n"
            f"**FAQ:** {question}\n\n"
            f"**Current answer:** {current_answer}\n\n"
            f"**New answer:** {new_answer}\n\n"
            "Type **YES** to confirm this update or **NO** to cancel."
        )

    return (
        "⚠️ This database update requires confirmation.\n\n"
        "Type **YES** to confirm or **NO** to cancel."
    )


# ============================================================
# EXECUTE FUNCTION
# ============================================================

def execute_function(function_name: str, args: Dict[str, Any]):
    """
    Execute a permitted function.
    """

    function = available_functions.get(function_name)

    if not function:
        raise ValueError(
            f"Function '{function_name}' is not available."
        )

    return function(**args)


# ============================================================
# CONFIRMATION HANDLER
# ============================================================

def handle_confirmation(session_id: str, message: str):
    """
    Handle YES / NO responses for pending database updates.
    """

    action = pending_actions.get(session_id)

    if not action:
        return None

    normalized = message.strip().lower()

    # --------------------------------------------------------
    # CANCEL
    # --------------------------------------------------------

    if normalized in {
        "no",
        "n",
        "cancel",
        "cancelled",
        "cancelled.",
    }:
        del pending_actions[session_id]

        return (
            "❌ Update cancelled.\n\n"
            "No changes were made to the database."
        )

    # --------------------------------------------------------
    # CONFIRM
    # --------------------------------------------------------

    if normalized in {
        "yes",
        "y",
        "confirm",
        "confirmed",
    }:
        function_name = action["function_name"]
        args = action["args"]

        try:
            result = execute_function(
                function_name,
                args,
            )

            del pending_actions[session_id]

            return format_write_result(
                function_name,
                result,
            )

        except Exception as error:
            del pending_actions[session_id]

            return (
                "❌ The database update could not be completed.\n\n"
                f"Error: {str(error)}"
            )

    # --------------------------------------------------------
    # NOT A VALID CONFIRMATION
    # --------------------------------------------------------

    return (
        "⚠️ I still need your confirmation.\n\n"
        "Type **YES** to apply the database update or "
        "**NO** to cancel it."
    )


# ============================================================
# FORMAT WRITE RESULT
# ============================================================

def format_write_result(function_name: str, result: Any) -> str:
    """
    Convert write-tool results into a user-friendly response.
    """

    if isinstance(result, dict):

        success = result.get("success")

        if success:
            message = result.get("message")

            if message:
                return f"✅ {message}"

            return (
                "✅ Database update completed successfully."
            )

        error = result.get("error")

        if error:
            return f"❌ Update failed: {error}"

    return (
        "✅ The database operation completed.\n\n"
        f"Result: {result}"
    )


# ============================================================
# AGENT
# ============================================================

def run_agent(user_prompt: str, session_id: str) -> str:

    # --------------------------------------------------------
    # CHECK FOR PENDING CONFIRMATION
    # --------------------------------------------------------

    confirmation_result = handle_confirmation(
        session_id,
        user_prompt,
    )

    if confirmation_result is not None:
        return confirmation_result

    # --------------------------------------------------------
    # START GEMINI CONVERSATION
    # --------------------------------------------------------

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part(
                    text=user_prompt
                )
            ],
        )
    ]

    # --------------------------------------------------------
    # AGENT LOOP
    # --------------------------------------------------------

    for _ in range(10):

        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=tools,
                temperature=0.2,
            ),
        )

        # ----------------------------------------------------
        # NORMAL TEXT RESPONSE
        # ----------------------------------------------------

        if not response.candidates:
            return (
                "I couldn't generate a response right now. "
                "Please try again."
            )

        candidate = response.candidates[0]

        if not candidate.content:
            return (
                "I couldn't generate a response right now."
            )

        contents.append(candidate.content)

        function_calls = []

        for part in candidate.content.parts:

            if getattr(part, "function_call", None):
                function_calls.append(
                    part.function_call
                )

        # ----------------------------------------------------
        # NO TOOL CALL
        # ----------------------------------------------------

        if not function_calls:

            text = response.text

            if text:
                return text

            return (
                "I couldn't generate a text response."
            )

        # ----------------------------------------------------
        # PROCESS TOOL CALLS
        # ----------------------------------------------------

        tool_responses = []

        for function_call in function_calls:

            function_name = function_call.name

            args = dict(
                function_call.args or {}
            )

            # ================================================
            # WRITE OPERATION
            # ================================================

            if function_name in WRITE_TOOLS:

                # Only one pending write per session.
                pending_actions[session_id] = {
                    "function_name": function_name,
                    "args": args,
                    "action_id": str(uuid.uuid4()),
                }

                confirmation_message = (
                    get_confirmation_message(
                        function_name,
                        args,
                    )
                )

                return confirmation_message

            # ================================================
            # READ OPERATION
            # ================================================

            try:

                result = execute_function(
                    function_name,
                    args,
                )

                tool_responses.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=function_name,
                            response={
                                "result": result
                            },
                        )
                    )
                )

            except Exception as error:

                tool_responses.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=function_name,
                            response={
                                "error": str(error)
                            },
                        )
                    )
                )

        # ----------------------------------------------------
        # SEND TOOL RESULTS BACK TO GEMINI
        # ----------------------------------------------------

        contents.append(
            types.Content(
                role="tool",
                parts=tool_responses,
            )
        )

    return (
        "I reached the maximum number of analysis steps. "
        "Please try asking the question again."
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "Paras Arts AI Data Agent",
        "status": "online",
        "mode": "read-write",
        "version": "2.0.0",
        "message": (
            "AI agent is connected to Paras Arts MongoDB "
            "with controlled read and write access."
        ),
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    try:
        db.command("ping")

        return {
            "status": "healthy",
            "database": "connected",
            "agent_mode": "read-write",
        }

    except Exception as error:

        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(error)}",
        )


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    if not request.session_id.strip():
        raise HTTPException(
            status_code=400,
            detail="session_id is required.",
        )

    try:

        answer = run_agent(
            request.message,
            request.session_id,
        )

        return ChatResponse(
            answer=answer
        )

    except Exception as error:

        import traceback

        print("=" * 60)
        print("AGENT ERROR")
        print(f"ERROR TYPE: {type(error).__name__}")
        print(f"ERROR: {error}")
        print("TRACEBACK:")
        traceback.print_exc()
        print("=" * 60)

        raise HTTPException(
            status_code=500,
            detail=(
                f"Agent error: {type(error).__name__}: {str(error)}"
            ),
        )