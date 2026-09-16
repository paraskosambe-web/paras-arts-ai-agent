import os
import uuid
import traceback
from typing import Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google import genai
from google.genai import types


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

MODEL = "gemini-3.6-flash"


# ============================================================
# IMPORT PARAS ARTS TOOLS
# ============================================================

from paras_tools import (
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
# FASTAPI
# ============================================================

app = FastAPI(
    title="Paras Arts AI Agent",
    version="1.0.0"
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
# PENDING WRITE ACTIONS
# ============================================================

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
# ALL AVAILABLE FUNCTIONS
# ============================================================

available_functions = {

    # --------------------------------------------------------
    # READ
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
    # WRITE
    # --------------------------------------------------------

    "update_paras_order_status":
        update_paras_order_status,

    "update_paras_payment_status":
        update_paras_payment_status,

    "update_paras_artwork_featured":
        update_paras_artwork_featured,

    "update_paras_service_price":
        update_paras_service_price,

    "update_paras_faq_answer":
        update_paras_faq_answer,
}


# ============================================================
# GEMINI FUNCTION DECLARATIONS
# ============================================================

function_declarations = [

    # ========================================================
    # ORDER SEARCH
    # ========================================================

    types.FunctionDeclaration(
        name="search_paras_orders",
        description=(
            "Search Paras Arts customer orders. "
            "Use this when the user asks to find, list, "
            "or inspect orders."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": (
                        "Optional order status. "
                        "Allowed values: Pending, Accepted, "
                        "In Progress, Completed, Cancelled."
                    )
                }
            }
        },
    ),


    # ========================================================
    # ORDER ANALYSIS
    # ========================================================

    types.FunctionDeclaration(
        name="analyze_paras_orders",
        description=(
            "Analyze Paras Arts order data including "
            "order counts and status distribution."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {}
        },
    ),


    # ========================================================
    # PAYMENT ANALYSIS
    # ========================================================

    types.FunctionDeclaration(
        name="analyze_paras_payments",
        description=(
            "Analyze payment status information "
            "for Paras Arts orders."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {}
        },
    ),


    # ========================================================
    # SKETCH TYPE ANALYSIS
    # ========================================================

    types.FunctionDeclaration(
        name="analyze_paras_sketch_types",
        description=(
            "Analyze the different sketch/service types "
            "requested through Paras Arts orders."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {}
        },
    ),


    # ========================================================
    # BUDGET ANALYSIS
    # ========================================================

    types.FunctionDeclaration(
        name="analyze_paras_budgets",
        description=(
            "Analyze customer budget information "
            "from Paras Arts orders."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {}
        },
    ),


    # ========================================================
    # ARTWORK SEARCH
    # ========================================================

    types.FunctionDeclaration(
        name="search_paras_artworks",
        description=(
            "Search Paras Arts artwork portfolio data."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": (
                        "Optional artwork category."
                    )
                },
                "featured": {
                    "type": "boolean",
                    "description": (
                        "Optional filter for featured artworks."
                    )
                }
            }
        },
    ),


    # ========================================================
    # ARTWORK ANALYSIS
    # ========================================================

    types.FunctionDeclaration(
        name="analyze_paras_artworks",
        description=(
            "Analyze Paras Arts artwork portfolio data."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {}
        },
    ),


    # ========================================================
    # SERVICE SEARCH
    # ========================================================

    types.FunctionDeclaration(
        name="search_paras_services",
        description=(
            "Search Paras Arts service information "
            "including service names and prices."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {}
        },
    ),


    # ========================================================
    # SERVICE ANALYSIS
    # ========================================================

    types.FunctionDeclaration(
        name="analyze_paras_services",
        description=(
            "Analyze Paras Arts service information."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {}
        },
    ),


    # ========================================================
    # FAQ SEARCH
    # ========================================================

    types.FunctionDeclaration(
        name="search_paras_faqs",
        description=(
            "Search Paras Arts FAQ information."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {}
        },
    ),


    # ========================================================
    # FAQ ANALYSIS
    # ========================================================

    types.FunctionDeclaration(
        name="analyze_paras_faqs",
        description=(
            "Analyze Paras Arts FAQ data."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {}
        },
    ),


    # ========================================================
    # BUSINESS SUMMARY
    # ========================================================

    types.FunctionDeclaration(
        name="get_paras_business_summary",
        description=(
            "Get an overall business summary "
            "from Paras Arts MongoDB data."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {}
        },
    ),


    # ========================================================
    # WRITE: ORDER STATUS
    # ========================================================

    types.FunctionDeclaration(
        name="update_paras_order_status",
        description=(
            "Update the status of a Paras Arts order. "
            "This operation requires user confirmation "
            "before execution."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": (
                        "Paras Arts order ID, for example PA-1234."
                    )
                },
                "new_status": {
                    "type": "string",
                    "description": (
                        "New order status. Allowed values: "
                        "Pending, Accepted, In Progress, "
                        "Completed, Cancelled."
                    )
                }
            },
            "required": [
                "order_id",
                "new_status"
            ]
        },
    ),


    # ========================================================
    # WRITE: PAYMENT STATUS
    # ========================================================

    types.FunctionDeclaration(
        name="update_paras_payment_status",
        description=(
            "Update payment status for a Paras Arts order. "
            "This operation requires user confirmation "
            "before execution."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": (
                        "Paras Arts order ID."
                    )
                },
                "new_payment_status": {
                    "type": "string",
                    "description": (
                        "New payment status. Allowed values: "
                        "Pending, Verified, Failed."
                    )
                }
            },
            "required": [
                "order_id",
                "new_payment_status"
            ]
        },
    ),


    # ========================================================
    # WRITE: ARTWORK FEATURED
    # ========================================================

    types.FunctionDeclaration(
        name="update_paras_artwork_featured",
        description=(
            "Change whether a Paras Arts artwork is featured. "
            "This operation requires user confirmation."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": (
                        "Exact artwork title."
                    )
                },
                "featured": {
                    "type": "boolean",
                    "description": (
                        "Whether the artwork should be featured."
                    )
                }
            },
            "required": [
                "title",
                "featured"
            ]
        },
    ),


    # ========================================================
    # WRITE: SERVICE PRICE
    # ========================================================

    types.FunctionDeclaration(
        name="update_paras_service_price",
        description=(
            "Change the price of a Paras Arts service. "
            "This operation requires user confirmation."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": (
                        "Exact service title."
                    )
                },
                "new_price": {
                    "type": "number",
                    "description": (
                        "New service price."
                    )
                }
            },
            "required": [
                "title",
                "new_price"
            ]
        },
    ),


    # ========================================================
    # WRITE: FAQ ANSWER
    # ========================================================

    types.FunctionDeclaration(
        name="update_paras_faq_answer",
        description=(
            "Update the answer to a Paras Arts FAQ. "
            "This operation requires user confirmation."
        ),
        parameters_json_schema={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": (
                        "Exact FAQ question."
                    )
                },
                "new_answer": {
                    "type": "string",
                    "description": (
                        "New FAQ answer."
                    )
                }
            },
            "required": [
                "question",
                "new_answer"
            ]
        },
    ),
]


# ============================================================
# GEMINI TOOL
# ============================================================

paras_tool = types.Tool(
    function_declarations=function_declarations
)


# ============================================================
# SYSTEM INSTRUCTIONS
# ============================================================

SYSTEM_PROMPT = """
You are the Paras Arts AI Business Data Agent.

You are connected to the Paras Arts MongoDB database.

Your job is to help the business owner search, analyze,
understand, and carefully update business data.

============================================================
READ OPERATIONS
============================================================

You can search and analyze:

- Orders
- Payments
- Sketch types
- Budgets
- Artworks
- Services
- FAQs
- Overall business information

Always use the appropriate MongoDB tool when the user asks
about actual Paras Arts database information.

Do not invent database values.

============================================================
WRITE OPERATIONS
============================================================

You can perform ONLY these controlled updates:

1. Update order status
2. Update payment status
3. Update artwork featured status
4. Update service price
5. Update FAQ answer

You cannot:

- Delete data
- Drop collections
- Drop the database
- Run arbitrary MongoDB queries
- Modify arbitrary fields
- Create arbitrary database commands

============================================================
CONFIRMATION
============================================================

Every write operation MUST require explicit confirmation.

Never directly execute a write operation simply because
the user requested it.

When a write tool is requested, prepare the action and ask
the user to confirm it.

The confirmation message will be handled by the application.

A confirmation such as:

YES
yes
Yes
confirm
confirmed

means the user approved the pending action.

A response such as:

NO
no
cancel
cancelled

means the user rejected the action.

============================================================
DATABASE PRIVACY
============================================================

Do not expose sensitive customer contact information such as:

- Phone numbers
- Email addresses
- Physical addresses
- Payment credentials
- Reference image URLs

Only provide information necessary to answer the user's
business question.

============================================================
RESPONSE STYLE
============================================================

Be concise and useful.

When reporting numbers, use clear formatting.

When analyzing business data, explain what the data means.

Do not claim that a database update happened unless the
write tool actually returned a successful result.

If a tool returns an error, clearly explain the error.

============================================================
IMPORTANT
============================================================

You are a controlled business data assistant.

Use MongoDB tools for real database information.

Do not hallucinate database records.
"""


# ============================================================
# EXECUTE FUNCTION
# ============================================================

def execute_function(
    function_name: str,
    args: Dict[str, Any]
):

    if function_name not in available_functions:
        raise ValueError(
            f"Unknown function: {function_name}"
        )

    function = available_functions[
        function_name
    ]

    return function(**args)


# ============================================================
# CONFIRMATION MESSAGE
# ============================================================

def get_confirmation_message(
    function_name: str,
    args: Dict[str, Any]
) -> str:

    if function_name == "update_paras_order_status":

        order_id = args.get("order_id")
        new_status = args.get("new_status")

        return (
            "⚠️ **Confirmation required**\n\n"
            f"Order: `{order_id}`\n"
            f"New status: **{new_status}**\n\n"
            "This will update the order in MongoDB.\n\n"
            "Reply **YES** to confirm or **NO** to cancel."
        )


    if function_name == "update_paras_payment_status":

        order_id = args.get("order_id")
        new_status = args.get(
            "new_payment_status"
        )

        return (
            "⚠️ **Confirmation required**\n\n"
            f"Order: `{order_id}`\n"
            f"New payment status: **{new_status}**\n\n"
            "This will update the payment status in MongoDB.\n\n"
            "Reply **YES** to confirm or **NO** to cancel."
        )


    if function_name == "update_paras_artwork_featured":

        title = args.get("title")
        featured = args.get("featured")

        state = (
            "Featured"
            if featured
            else "Not Featured"
        )

        return (
            "⚠️ **Confirmation required**\n\n"
            f"Artwork: **{title}**\n"
            f"New featured status: **{state}**\n\n"
            "This will update the artwork in MongoDB.\n\n"
            "Reply **YES** to confirm or **NO** to cancel."
        )


    if function_name == "update_paras_service_price":

        title = args.get("title")
        price = args.get("new_price")

        return (
            "⚠️ **Confirmation required**\n\n"
            f"Service: **{title}**\n"
            f"New price: **₹{price}**\n\n"
            "This will update the service price in MongoDB.\n\n"
            "Reply **YES** to confirm or **NO** to cancel."
        )


    if function_name == "update_paras_faq_answer":

        question = args.get("question")
        answer = args.get("new_answer")

        return (
            "⚠️ **Confirmation required**\n\n"
            f"FAQ: **{question}**\n\n"
            f"New answer:\n{answer}\n\n"
            "This will update the FAQ in MongoDB.\n\n"
            "Reply **YES** to confirm or **NO** to cancel."
        )


    return (
        "⚠️ Confirmation required.\n\n"
        "Reply **YES** to confirm or **NO** to cancel."
    )


# ============================================================
# FORMAT WRITE RESULT
# ============================================================

def format_write_result(
    function_name: str,
    result: Any
) -> str:

    if isinstance(result, dict):

        if result.get("success") is True:

            return (
                "✅ **Database update successful.**\n\n"
                f"{result}"
            )

        if result.get("success") is False:

            return (
                "❌ **Database update failed.**\n\n"
                f"{result}"
            )

    return (
        "✅ **Database operation completed.**\n\n"
        f"{result}"
    )


# ============================================================
# HANDLE CONFIRMATION
# ============================================================

def handle_confirmation(
    session_id: str,
    message: str
):

    action = pending_actions.get(
        session_id
    )

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
        "reject",
        "rejected"
    }:

        del pending_actions[
            session_id
        ]

        return (
            "❌ Action cancelled.\n\n"
            "No database changes were made."
        )


    # --------------------------------------------------------
    # CONFIRM
    # --------------------------------------------------------

    if normalized not in {
        "yes",
        "y",
        "confirm",
        "confirmed"
    }:

        return (
            "Please reply **YES** to confirm "
            "or **NO** to cancel."
        )


    function_name = action[
        "function_name"
    ]

    args = action[
        "args"
    ]


    print(
        f"[CONFIRMED WRITE] "
        f"{function_name} {args}"
    )


    try:

        result = execute_function(
            function_name,
            args
        )

        del pending_actions[
            session_id
        ]

        return format_write_result(
            function_name,
            result
        )

    except Exception as error:

        print(
            "[WRITE ERROR]"
        )

        print(
            traceback.format_exc()
        )

        del pending_actions[
            session_id
        ]

        return (
            "❌ **Database update failed.**\n\n"
            f"Error: `{str(error)}`"
        )


# ============================================================
# RUN AI AGENT
# ============================================================

def run_agent(
    message: str,
    session_id: str
) -> str:

    # --------------------------------------------------------
    # CHECK PENDING CONFIRMATION FIRST
    # --------------------------------------------------------

    if session_id in pending_actions:

        confirmation_result = handle_confirmation(
            session_id,
            message
        )

        if confirmation_result:
            return confirmation_result


    # --------------------------------------------------------
    # INITIAL USER CONTENT
    # --------------------------------------------------------

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=message
                )
            ]
        )
    ]


    # --------------------------------------------------------
    # AGENT LOOP
    # --------------------------------------------------------

    for iteration in range(10):

        print(
            f"[AGENT LOOP] iteration={iteration + 1}"
        )


        # ----------------------------------------------------
        # CALL GEMINI
        # ----------------------------------------------------

        response = client.models.generate_content(

            model=MODEL,

            contents=contents,

            config=types.GenerateContentConfig(

                system_instruction=SYSTEM_PROMPT,

                tools=[
                    paras_tool
                ],

                temperature=0.2,

                automatic_function_calling=(
                    types.AutomaticFunctionCallingConfig(
                        disable=True
                    )
                ),
            ),
        )


        # ----------------------------------------------------
        # SAFETY CHECK
        # ----------------------------------------------------

        if not response.candidates:

            return (
                "I couldn't generate a response."
            )


        candidate = response.candidates[0]


        # ----------------------------------------------------
        # CHECK FUNCTION CALLS
        # ----------------------------------------------------

        function_calls = (
            response.function_calls
        )


        # ----------------------------------------------------
        # NO FUNCTION CALL
        # ----------------------------------------------------

        if not function_calls:

            text = response.text

            if text:
                return text

            return (
                "I couldn't generate a response."
            )


        # ----------------------------------------------------
        # IMPORTANT:
        # KEEP GEMINI'S ORIGINAL MODEL CONTENT
        # ----------------------------------------------------

        if candidate.content:

            contents.append(
                candidate.content
            )


        # ----------------------------------------------------
        # PROCESS FUNCTION CALLS
        # ----------------------------------------------------

        tool_responses = []


        for function_call in function_calls:

            function_name = (
                function_call.name
            )

            args = dict(
                function_call.args or {}
            )


            print(
                f"[TOOL CALL] "
                f"{function_name} "
                f"{args}"
            )


            # =================================================
            # WRITE OPERATION
            # =================================================

            if function_name in WRITE_TOOLS:

                pending_actions[
                    session_id
                ] = {

                    "function_name":
                        function_name,

                    "args":
                        args,

                    "action_id":
                        str(
                            uuid.uuid4()
                        ),
                }


                confirmation_message = (
                    get_confirmation_message(
                        function_name,
                        args
                    )
                )


                return confirmation_message


            # =================================================
            # READ OPERATION
            # =================================================

            try:

                result = execute_function(
                    function_name,
                    args
                )


                print(
                    f"[TOOL RESULT] "
                    f"{function_name}: "
                    f"{result}"
                )


                # ------------------------------------------------
                # IMPORTANT:
                # Do NOT pass id= here.
                #
                # google-genai 2.23.0 does not accept
                # id= in Part.from_function_response().
                # ------------------------------------------------

                tool_responses.append(

                    types.Part.from_function_response(

                        name=function_name,

                        response={
                            "result": result
                        },
                    )
                )


            except Exception as error:

                print(
                    f"[TOOL ERROR] "
                    f"{function_name}: "
                    f"{error}"
                )

                print(
                    traceback.format_exc()
                )


                tool_responses.append(

                    types.Part.from_function_response(

                        name=function_name,

                        response={
                            "error": str(error)
                        },
                    )
                )


        # ----------------------------------------------------
        # SEND FUNCTION RESULTS BACK TO GEMINI
        #
        # Your API previously rejected role="tool".
        #
        # Therefore we send the function response using
        # a user Content object.
        # ----------------------------------------------------

        if tool_responses:

            contents.append(

                types.Content(

                    role="user",

                    parts=tool_responses
                )
            )


    # --------------------------------------------------------
    # MAX ITERATIONS
    # --------------------------------------------------------

    return (
        "I reached the maximum number of tool operations "
        "for this request. Please try the question again."
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "Paras Arts AI Agent",
        "mode": "controlled-read-write",
        "model": MODEL,
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# CHAT
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        message = request.message.strip()

        session_id = request.session_id.strip()


        if not message:

            return {
                "answer": "Please enter a message."
            }


        if not session_id:

            return {
                "answer": (
                    "A session ID is required."
                )
            }


        print(
            "\n=============================="
        )

        print(
            "[USER]"
        )

        print(
            message
        )

        print(
            f"[SESSION] {session_id}"
        )

        print(
            "=============================="
        )


        answer = run_agent(
            message,
            session_id
        )


        print(
            "[ASSISTANT]"
        )

        print(
            answer
        )


        return {
            "answer": answer
        }


    except Exception as error:

        print(
            "\n=============================="
        )

        print(
            "[API ERROR]"
        )

        print(
            traceback.format_exc()
        )

        print(
            "=============================="
        )


        return {
            "answer": (
                "Agent error: "
                f"{type(error).__name__}: "
                f"{str(error)}"
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
        reload=True,
    )