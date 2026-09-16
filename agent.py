import os
import json

from dotenv import load_dotenv
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
    db,
)


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in .env")


# ============================================================
# GEMINI
# ============================================================

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-3.6-flash"


# ============================================================
# TOOL DEFINITIONS
# ============================================================

tools = types.Tool(
    function_declarations=[
        # ----------------------------
        # READ / ANALYSIS TOOLS
        # ----------------------------

        types.FunctionDeclaration(
            name="search_paras_orders",
            description="Search Paras Arts orders. Optionally filter by order status.",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Optional order status such as Pending, Accepted, In Progress, Completed, or Cancelled."
                    }
                }
            },
        ),

        types.FunctionDeclaration(
            name="analyze_paras_orders",
            description="Analyze the total number of Paras Arts orders and group them by status.",
            parameters_json_schema={
                "type": "object",
                "properties": {}
            },
        ),

        types.FunctionDeclaration(
            name="analyze_paras_payments",
            description="Analyze Paras Arts orders by payment status.",
            parameters_json_schema={
                "type": "object",
                "properties": {}
            },
        ),

        types.FunctionDeclaration(
            name="analyze_paras_sketch_types",
            description="Analyze Paras Arts orders by sketch type.",
            parameters_json_schema={
                "type": "object",
                "properties": {}
            },
        ),

        types.FunctionDeclaration(
            name="analyze_paras_budgets",
            description="Analyze requested order budgets. These values are not revenue.",
            parameters_json_schema={
                "type": "object",
                "properties": {}
            },
        ),

        types.FunctionDeclaration(
            name="search_paras_artworks",
            description="Search Paras Arts artworks by category or featured status.",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional artwork category."
                    },
                    "featured": {
                        "type": "boolean",
                        "description": "Optional featured filter."
                    }
                }
            },
        ),

        types.FunctionDeclaration(
            name="analyze_paras_artworks",
            description="Analyze Paras Arts artworks by category and featured status.",
            parameters_json_schema={
                "type": "object",
                "properties": {}
            },
        ),

        types.FunctionDeclaration(
            name="search_paras_services",
            description="Search Paras Arts services by title.",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Optional service title."
                    }
                }
            },
        ),

        types.FunctionDeclaration(
            name="analyze_paras_services",
            description="Analyze Paras Arts services and their starting prices.",
            parameters_json_schema={
                "type": "object",
                "properties": {}
            },
        ),

        types.FunctionDeclaration(
            name="search_paras_faqs",
            description="Search Paras Arts FAQs by category or keyword.",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional FAQ category."
                    },
                    "keyword": {
                        "type": "string",
                        "description": "Optional keyword to search in questions and answers."
                    }
                }
            },
        ),

        types.FunctionDeclaration(
            name="analyze_paras_faqs",
            description="Analyze Paras Arts FAQs by category.",
            parameters_json_schema={
                "type": "object",
                "properties": {}
            },
        ),

        types.FunctionDeclaration(
            name="get_paras_business_summary",
            description="Get an overall read-only summary of the Paras Arts database.",
            parameters_json_schema={
                "type": "object",
                "properties": {}
            },
        ),

        # ----------------------------
        # WRITE TOOLS
        # ----------------------------

        types.FunctionDeclaration(
            name="update_paras_order_status",
            description="Update the status of one Paras Arts order. Only use after explicit user confirmation.",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Paras Arts order ID."
                    },
                    "new_status": {
                        "type": "string",
                        "description": "New order status."
                    }
                },
                "required": ["order_id", "new_status"]
            },
        ),

        types.FunctionDeclaration(
            name="update_paras_payment_status",
            description="Update the payment status of one Paras Arts order. Only use after explicit user confirmation.",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Paras Arts order ID."
                    },
                    "new_payment_status": {
                        "type": "string",
                        "description": "New payment status."
                    }
                },
                "required": ["order_id", "new_payment_status"]
            },
        ),

        types.FunctionDeclaration(
            name="update_paras_artwork_featured",
            description="Change whether a Paras Arts artwork is featured. Only use after explicit user confirmation.",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Artwork title."
                    },
                    "featured": {
                        "type": "boolean",
                        "description": "Whether the artwork should be featured."
                    }
                },
                "required": ["title", "featured"]
            },
        ),

        types.FunctionDeclaration(
            name="update_paras_service_price",
            description="Update the starting price of a Paras Arts service. Only use after explicit user confirmation.",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Service title."
                    },
                    "new_price": {
                        "type": "number",
                        "description": "New starting price."
                    }
                },
                "required": ["title", "new_price"]
            },
        ),

        types.FunctionDeclaration(
            name="update_paras_faq_answer",
            description="Update the answer of a Paras Arts FAQ. Only use after explicit user confirmation.",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Exact FAQ question."
                    },
                    "new_answer": {
                        "type": "string",
                        "description": "New FAQ answer."
                    }
                },
                "required": ["question", "new_answer"]
            },
        ),
    ]
)


# ============================================================
# FUNCTION MAP
# ============================================================

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
    "get_paras_business_summary": get_paras_business_summary,

    "update_paras_order_status": update_paras_order_status,
    "update_paras_payment_status": update_paras_payment_status,
    "update_paras_artwork_featured": update_paras_artwork_featured,
    "update_paras_service_price": update_paras_service_price,
    "update_paras_faq_answer": update_paras_faq_answer,
}


WRITE_TOOLS = {
    "update_paras_order_status",
    "update_paras_payment_status",
    "update_paras_artwork_featured",
    "update_paras_service_price",
    "update_paras_faq_answer",
}


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are the Paras Arts AI Data Analyst and Data Management Agent.

You work with the real Paras Arts MongoDB database.

You can:
1. Search business data.
2. Analyze business data.
3. Answer questions using MongoDB data.
4. Perform a small set of controlled database updates.

IMPORTANT SECURITY RULES:

- Never access the admins collection.
- Never expose passwords, authentication credentials, phone numbers,
  email addresses, physical addresses, or reference image URLs.
- Do not invent database information.
- Use MongoDB tools when the user's question requires actual database data.
- Requested order budgets are not revenue.
- Do not perform delete operations.
- Do not execute arbitrary MongoDB commands.

WRITE OPERATIONS:

Available controlled writes are:
- Change order status.
- Change payment status.
- Change artwork featured status.
- Change service starting price.
- Change FAQ answer.

A write operation must only happen after the Python application
obtains explicit confirmation from the user.

Do not claim that a write happened unless the write tool actually
returns a successful result.
"""


# ============================================================
# CONFIRMATION DATA HELPERS
# ============================================================

def get_order_for_confirmation(order_id):
    return db["orders"].find_one(
        {"orderId": order_id},
        {
            "_id": 0,
            "orderId": 1,
            "fullName": 1,
            "sketchType": 1,
            "paperSize": 1,
            "status": 1,
            "paymentStatus": 1,
        },
    )


def get_artwork_for_confirmation(title):
    return db["artworks"].find_one(
        {"title": title},
        {
            "_id": 0,
            "title": 1,
            "category": 1,
            "featured": 1,
        },
    )


def get_service_for_confirmation(title):
    return db["services"].find_one(
        {"title": title},
        {
            "_id": 0,
            "title": 1,
            "priceFrom": 1,
        },
    )


def get_faq_for_confirmation(question):
    return db["faqs"].find_one(
        {"question": question},
        {
            "_id": 0,
            "question": 1,
            "answer": 1,
        },
    )


# ============================================================
# CONFIRMATION
# ============================================================

def ask_for_confirmation(function_name, args):

    print("\n" + "=" * 55)
    print("⚠️  WRITE OPERATION REQUESTED")
    print("=" * 55)

    if function_name == "update_paras_order_status":

        order_id = args["order_id"]
        new_status = args["new_status"]

        order = get_order_for_confirmation(order_id)

        if not order:
            print(f"Order {order_id} was not found.")
            return False

        print(f"Order ID       : {order_id}")
        print(f"Customer       : {order.get('fullName', 'N/A')}")
        print(f"Sketch Type    : {order.get('sketchType', 'N/A')}")
        print(f"Current Status : {order.get('status', 'N/A')}")
        print(f"New Status     : {new_status}")

    elif function_name == "update_paras_payment_status":

        order_id = args["order_id"]
        new_status = args["new_payment_status"]

        order = get_order_for_confirmation(order_id)

        if not order:
            print(f"Order {order_id} was not found.")
            return False

        print(f"Order ID          : {order_id}")
        print(f"Current Payment   : {order.get('paymentStatus', 'N/A')}")
        print(f"New Payment       : {new_status}")

    elif function_name == "update_paras_artwork_featured":

        title = args["title"]
        featured = args["featured"]

        artwork = get_artwork_for_confirmation(title)

        if not artwork:
            print(f"Artwork '{title}' was not found.")
            return False

        print(f"Artwork           : {title}")
        print(f"Category          : {artwork.get('category', 'N/A')}")
        print(f"Current Featured  : {artwork.get('featured', False)}")
        print(f"New Featured      : {featured}")

    elif function_name == "update_paras_service_price":

        title = args["title"]
        new_price = args["new_price"]

        service = get_service_for_confirmation(title)

        if not service:
            print(f"Service '{title}' was not found.")
            return False

        print(f"Service           : {title}")
        print(f"Current Price     : ₹{service.get('priceFrom', 'N/A')}")
        print(f"New Price         : ₹{new_price}")

    elif function_name == "update_paras_faq_answer":

        question = args["question"]
        new_answer = args["new_answer"]

        faq = get_faq_for_confirmation(question)

        if not faq:
            print("FAQ with that question was not found.")
            return False

        print(f"FAQ Question      : {question}")
        print(f"Current Answer    : {faq.get('answer', 'N/A')}")
        print(f"New Answer        : {new_answer}")

    else:
        return False

    print("=" * 55)
    print("Type YES to confirm this database change.")
    print("Type NO to cancel.")
    print("=" * 55)

    while True:
        confirmation = input("Confirmation: ").strip().upper()

        if confirmation == "YES":
            print("✅ Confirmed.")
            return True

        if confirmation == "NO":
            print("❌ Write operation cancelled.")
            return False

        print("Please type YES or NO.")


# ============================================================
# AGENT REQUEST
# ============================================================

def run_agent(user_prompt):

    response = client.models.generate_content(
        model=MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[tools],
            temperature=0,
        ),
    )

    # --------------------------------------------------------
    # Handle function calls
    # --------------------------------------------------------

    while response.function_calls:

        function_call = response.function_calls[0]

        function_name = function_call.name
        args = dict(function_call.args or {})

        print(f"\n🔧 Tool selected: {function_name}")

        if function_name not in available_functions:
            return "The requested tool is not available."

        function_to_call = available_functions[function_name]

        # ----------------------------------------------------
        # WRITE OPERATION
        # ----------------------------------------------------

        if function_name in WRITE_TOOLS:

            confirmed = ask_for_confirmation(
                function_name,
                args,
            )

            if not confirmed:
                return "The database change was cancelled."

        # ----------------------------------------------------
        # EXECUTE TOOL
        # ----------------------------------------------------

        try:
            result = function_to_call(**args)

        except Exception as e:
            return f"Tool execution error: {e}"

        print("\n📊 Tool result:")
        print(result)

        # ----------------------------------------------------
        # Send result back to Gemini
        # ----------------------------------------------------

        response = client.models.generate_content(
            model=MODEL,
            contents=[
                user_prompt,
                types.Part.from_function_response(
                    name=function_name,
                    response={
                        "result": result
                    },
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[tools],
                temperature=0,
            ),
        )

    return response.text


# ============================================================
# MAIN CHAT LOOP
# ============================================================

def main():

    print("\n======================================")
    print(" Paras Arts AI Data Agent")
    print("======================================")
    print("MongoDB: test")
    print(f"Gemini Model: {MODEL}")
    print("\nAI Data Analyst + Data Management Agent")
    print("Type 'exit' to quit.")
    print("======================================")

    while True:

        try:
            user_prompt = input("\nYou: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\n\nAgent stopped.")
            break

        if not user_prompt:
            continue

        if user_prompt.lower() in {
            "exit",
            "quit",
            "q",
        }:
            print("\nAgent stopped.")
            break

        try:
            answer = run_agent(user_prompt)

            print("\n🤖 Agent:")
            print(answer)

        except Exception as e:
            print("\n❌ Error:")
            print(e)


# ============================================================
# START PROGRAM
# ============================================================

if __name__ == "__main__":
    main()