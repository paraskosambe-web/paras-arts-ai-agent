import os
import json
import math
import time
import random
from typing import Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from openai import OpenAI
from google.genai import types

from paras_tools import (
    search_paras_orders,
    analyze_paras_orders,
    analyze_paras_order_trends,
    analyze_paras_order_segments,
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
    generate_paras_business_performance_report,
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

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is missing from environment variables."
    )


# ============================================================
# OPENROUTER CLIENT
# ============================================================

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

# Keep this configurable through deployment environment variables.
MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openrouter/free"
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
    version="2.2.0",
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
    "analyze_paras_order_trends": analyze_paras_order_trends,
    "analyze_paras_order_segments": analyze_paras_order_segments,
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
    "generate_paras_business_performance_report": generate_paras_business_performance_report,

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
# FUNCTION DECLARATIONS
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
        name="analyze_paras_order_trends",
        description=(
            "Analyze order volume over time for a daily, weekly, or monthly period. "
            "Use for trend questions and requests to chart orders over time. "
            "Only dated orders inside the selected window are counted."
        ),
        parameters={
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "enum": ["day", "week", "month"],
                    "description": "Time bucket for the trend.",
                },
                "periods": {
                    "type": "integer",
                    "description": "Number of buckets to include, from 2 to 24.",
                },
            },
        },
    ),

    types.FunctionDeclaration(
        name="analyze_paras_order_segments",
        description=(
            "Compare order counts or average requested budget across the safe dimensions "
            "status, paymentStatus, or sketchType. Use for questions like which sketch "
            "type has the highest average requested budget. Requested budget is not revenue."
        ),
        parameters={
            "type": "object",
            "properties": {
                "dimension": {
                    "type": "string",
                    "enum": ["status", "paymentStatus", "sketchType"],
                },
                "metric": {
                    "type": "string",
                    "enum": ["count", "average_budget"],
                },
            },
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

    types.FunctionDeclaration(
        name="generate_paras_business_performance_report",
        description=(
            "Generate one comprehensive, privacy-safe report snapshot for Paras Arts: "
            "all-time order and payment status, verified revenue only when reliable paid-amount "
            "data exists, artwork catalog categories, service-demand fields, customer touchpoint "
            "counts, newsletter status when available, data-quality and bottleneck counts, and "
            "chart payloads. Use this single tool for whole-business or comprehensive performance "
            "report requests. It returns no customer contact details."
        ),
        parameters={"type": "object", "properties": {}},
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
# OPENROUTER TOOL SCHEMAS
# ============================================================

def openrouter_function_schema(declaration):
    schema = declaration.model_dump(mode="json", exclude_none=True)

    def normalize_types(value):
        if isinstance(value, dict):
            return {
                key: (
                    item.lower()
                    if key == "type" and isinstance(item, str)
                    else normalize_types(item)
                )
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [normalize_types(item) for item in value]
        return value

    return normalize_types(schema)


OPENROUTER_TOOLS = [
    {
        "type": "function",
        "function": openrouter_function_schema(declaration),
    }
    for declaration in function_declarations
]


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
- Analyze order volume trends over time
- Compare order segments by status, payment status, or sketch type
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
- Generate a comprehensive business performance report

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

Never call requested order budgets revenue or sales. Only report actual
revenue if the database contains a verified payment amount field.

For trend or chart requests, use the relevant analysis tool and explain
notable changes only when supported by its returned values.

For decision questions, give a practical recommendation backed by database
facts, show the calculation or comparison used, and state when the available
data is too limited to justify a confident conclusion. Do not claim that one
business measure caused another without evidence.

============================================================
RESPONSE STYLE
============================================================

Give concise, useful and well-formatted responses.

Prefer:

- Short headings
- Bullet points
- Small tables when useful
- Put every Markdown table row on its own line; never compress a table into one line.
- Clear numbers
- Short explanations

Avoid unnecessarily long responses.

When reporting database results, distinguish between:

- Actual database facts
- Calculations based on database data
- General explanations

For requests for a comprehensive business report, use
generate_paras_business_performance_report once. Build the response from its returned
metrics, explain every unavailable metric, and give exactly five actionable
recommendations tied to observed counts or clearly stated data limitations.
Do not infer revenue from budgets, catalog prices, or order counts.

Never claim that a database modification happened until the
backend confirms that it was successfully executed.
"""


# ============================================================
# RETRY CONFIGURATION
# ============================================================

MAX_OPENROUTER_RETRIES = 3

RETRYABLE_ERROR_TEXT = (
    "503",
    "unavailable",
    "service unavailable",
    "temporarily unavailable",
    "overloaded",
    "429",
    "resource exhausted",
    "rate limit",
    "timeout",
    "timed out",
)


def is_retryable_openrouter_error(error: Exception) -> bool:
    """
    Determine whether an exception appears to be a temporary
    OpenRouter availability or rate-limit problem.
    """

    error_text = str(error).lower()

    return any(
        marker.lower() in error_text
        for marker in RETRYABLE_ERROR_TEXT
    )


# ============================================================
# OPENROUTER CALL WITH RETRY / BACKOFF
# ============================================================

def generate_with_retry(contents):
    last_error = None

    for attempt in range(MAX_OPENROUTER_RETRIES + 1):

        try:
            return client.chat.completions.create(
                model=MODEL,
                messages=contents,
                tools=OPENROUTER_TOOLS,
                tool_choice="auto",
                temperature=0.2,
                max_tokens=2600,
            )

        except Exception as error:

            last_error = error

            if not is_retryable_openrouter_error(error):
                raise

            if attempt >= MAX_OPENROUTER_RETRIES:
                raise

            delay = (
                (2 ** attempt)
                + random.uniform(0.2, 0.7)
            )

            print(
                f"[OpenRouter] Temporary error. "
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


def wants_visualization(message: str) -> bool:
    keywords = ("chart", "graph", "plot", "visualiz", "diagram", "pie chart", "donut")
    normalized = message.lower()
    return any(keyword in normalized for keyword in keywords)


def collect_visualizations(result):
    if not isinstance(result, dict):
        return []
    candidates = result.get("visualizations", [])
    if not candidates and result.get("visualization"):
        candidates = [result["visualization"]]
    if not isinstance(candidates, list):
        return []

    safe = []
    for chart in candidates[:6]:
        if not isinstance(chart, dict) or chart.get("type") not in {"bar", "line", "donut"}:
            continue
        rows = chart.get("data", [])
        if not isinstance(rows, list):
            continue
        safe.append({
            "type": chart["type"],
            "title": str(chart.get("title", "Data insight"))[:90],
            "value_label": str(chart.get("value_label", "Value"))[:40],
            "currency": chart.get("currency") if chart.get("currency") == "INR" else None,
            "data": [
                {"label": str(row.get("label", ""))[:60], "value": row.get("value", 0)}
                for row in rows[:30]
                if isinstance(row, dict)
                and isinstance(row.get("value", 0), (int, float))
                and math.isfinite(float(row.get("value", 0)))
            ],
        })
    return safe


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
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": message},
    ]
    include_visualizations = wants_visualization(message)
    visualizations = []

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
                f"[OpenRouter] Request failed: "
                f"{type(error).__name__}: {error}"
            )

            if is_retryable_openrouter_error(error):

                return (
                    "OpenRouter is temporarily unavailable right now. "
                    "Please try again in a few seconds."
                )

            return (
                "The AI agent encountered an error while "
                "processing your request."
            )

        # ----------------------------------------------------
        # NO FUNCTION CALL
        # ----------------------------------------------------

        assistant_message = response.choices[0].message
        function_calls = assistant_message.tool_calls or []

        if not function_calls:

            text = assistant_message.content

            if text:
                return {
                    "answer": text.strip(),
                    "visualizations": visualizations,
                }

            return (
                "I couldn't generate a response "
                "for that request."
            )

        # ----------------------------------------------------
        contents.append(assistant_message.model_dump(exclude_none=True))

        # ----------------------------------------------------
        # PROCESS FUNCTION CALLS
        # ----------------------------------------------------

        for function_call in function_calls:

            tool_name = function_call.function.name

            try:
                args = json.loads(function_call.function.arguments or "{}")
            except (TypeError, json.JSONDecodeError):
                args = {}

            print(
                f"[Agent] Function requested: "
                f"{tool_name} | args={args}"
            )

            # ------------------------------------------------
            # UNKNOWN TOOL
            # ------------------------------------------------

            if tool_name not in available_functions:

                contents.append({
                    "role": "tool",
                    "tool_call_id": function_call.id,
                    "content": json.dumps({"error": "Unknown function."}),
                })

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

                if include_visualizations:
                    visualizations.extend(collect_visualizations(result))

                print(
                    f"[Tool] {tool_name} executed successfully."
                )

                contents.append({
                    "role": "tool",
                    "tool_call_id": function_call.id,
                    "content": json.dumps({"result": result}, default=str),
                })

            except Exception as error:

                print(
                    f"[Tool] {tool_name} failed: "
                    f"{type(error).__name__}: {error}"
                )

                contents.append({
                    "role": "tool",
                    "tool_call_id": function_call.id,
                    "content": json.dumps({
                        "error": "The requested database operation failed."
                    }),
                })

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
        "version": "2.2.0",
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

        result = run_agent(
            message=message,
            session_id=session_id,
        )

        if isinstance(result, dict):
            return result
        return {"answer": result, "visualizations": []}

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
