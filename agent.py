import os
import time
import random

from dotenv import load_dotenv
from google import genai
from google.genai import types

from paras_tools import (
    db,

    # Read / analysis tools
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

    # Write tools
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
        "GEMINI_API_KEY is missing from your .env file."
    )


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# GEMINI MODELS
# ============================================================

# Primary model first.
# If temporarily unavailable, move to the next model.

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
]

MAX_RETRIES_PER_MODEL = 1


# ============================================================
# TOOL DECLARATIONS
# ============================================================

tools = types.Tool(
    function_declarations=[

        # ----------------------------------------------------
        # ORDERS
        # ----------------------------------------------------

        {
            "name": "search_paras_orders",
            "description": (
                "Search Paras Arts orders using safe filters "
                "such as status, payment status, sketch type, "
                "or order ID."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "status": {
                        "type": "STRING",
                        "description": "Optional order status."
                    },
                    "payment_status": {
                        "type": "STRING",
                        "description": "Optional payment status."
                    },
                    "sketch_type": {
                        "type": "STRING",
                        "description": "Optional sketch type."
                    },
                    "order_id": {
                        "type": "STRING",
                        "description": "Optional order ID."
                    }
                }
            }
        },

        {
            "name": "analyze_paras_orders",
            "description": (
                "Analyze Paras Arts orders and return total "
                "orders and order status counts."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {}
            }
        },

        {
            "name": "analyze_paras_payments",
            "description": (
                "Analyze payment status counts for Paras Arts orders."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {}
            }
        },

        {
            "name": "analyze_paras_sketch_types",
            "description": (
                "Analyze Paras Arts orders by sketch type."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {}
            }
        },

        {
            "name": "analyze_paras_budgets",
            "description": (
                "Analyze customer budget values from Paras Arts "
                "orders. This is not revenue."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {}
            }
        },

        # ----------------------------------------------------
        # ARTWORKS
        # ----------------------------------------------------

        {
            "name": "search_paras_artworks",
            "description": (
                "Search Paras Arts artworks using category "
                "or featured status filters."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "category": {
                        "type": "STRING",
                        "description": "Optional artwork category."
                    },
                    "featured": {
                        "type": "BOOLEAN",
                        "description": "Optional featured filter."
                    }
                }
            }
        },

        {
            "name": "analyze_paras_artworks",
            "description": (
                "Analyze Paras Arts artwork counts and categories."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {}
            }
        },

        # ----------------------------------------------------
        # SERVICES
        # ----------------------------------------------------

        {
            "name": "search_paras_services",
            "description": (
                "Search Paras Arts services by title."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "title": {
                        "type": "STRING",
                        "description": "Optional service title."
                    }
                }
            }
        },

        {
            "name": "analyze_paras_services",
            "description": (
                "Analyze Paras Arts service data."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {}
            }
        },

        # ----------------------------------------------------
        # FAQS
        # ----------------------------------------------------

        {
            "name": "search_paras_faqs",
            "description": (
                "Search Paras Arts FAQs by category or keyword."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "category": {
                        "type": "STRING",
                        "description": "Optional FAQ category."
                    },
                    "keyword": {
                        "type": "STRING",
                        "description": "Optional keyword."
                    }
                }
            }
        },

        {
            "name": "analyze_paras_faqs",
            "description": (
                "Analyze Paras Arts FAQ data."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {}
            }
        },

        # ----------------------------------------------------
        # BUSINESS SUMMARY
        # ----------------------------------------------------

        {
            "name": "get_paras_business_summary",
            "description": (
                "Get a high-level summary of Paras Arts business "
                "data including orders, artworks, services, FAQs, "
                "testimonials, messages, and newsletters."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {}
            }
        },

        # ----------------------------------------------------
        # WRITE TOOLS
        # ----------------------------------------------------

        {
            "name": "update_paras_order_status",
            "description": (
                "Update the status of a Paras Arts order."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "order_id": {
                        "type": "STRING"
                    },
                    "new_status": {
                        "type": "STRING"
                    }
                },
                "required": [
                    "order_id",
                    "new_status"
                ]
            }
        },

        {
            "name": "update_paras_payment_status",
            "description": (
                "Update the payment status of a Paras Arts order."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "order_id": {
                        "type": "STRING"
                    },
                    "new_payment_status": {
                        "type": "STRING"
                    }
                },
                "required": [
                    "order_id",
                    "new_payment_status"
                ]
            }
        },

        {
            "name": "update_paras_artwork_featured",
            "description": (
                "Update whether a Paras Arts artwork is featured."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "title": {
                        "type": "STRING"
                    },
                    "featured": {
                        "type": "BOOLEAN"
                    }
                },
                "required": [
                    "title",
                    "featured"
                ]
            }
        },

        {
            "name": "update_paras_service_price",
            "description": (
                "Update the starting price of a Paras Arts service."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "title": {
                        "type": "STRING"
                    },
                    "new_price": {
                        "type": "NUMBER"
                    }
                },
                "required": [
                    "title",
                    "new_price"
                ]
            }
        },

        {
            "name": "update_paras_faq_answer",
            "description": (
                "Update the answer to a Paras Arts FAQ."
            ),
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "question": {
                        "type": "STRING"
                    },
                    "new_answer": {
                        "type": "STRING"
                    }
                },
                "required": [
                    "question",
                    "new_answer"
                ]
            }
        },
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
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are the Paras Arts AI Data Analyst and Data Management Agent.

You work with the Paras Arts MongoDB database.

Your responsibilities:

1. Search and analyze Paras Arts business data.
2. Answer questions using actual database data.
3. Perform only approved database updates when explicitly
   confirmed by the Python application.

DATABASE SECURITY:

- NEVER access the admins collection.
- NEVER reveal passwords or credentials.
- NEVER reveal customer phone numbers.
- NEVER reveal customer email addresses.
- NEVER reveal customer physical addresses.
- NEVER reveal reference image URLs.
- NEVER execute arbitrary MongoDB commands.
- NEVER delete database records.
- NEVER modify fields outside the approved write tools.
- NEVER invent database information.

DATA INTERPRETATION:

- Customer budget is NOT revenue.
- Payment status is NOT order status.
- If the database does not contain enough information, say so.
- Do not invent values.

READ OPERATIONS:

You may use the available search and analysis tools to retrieve
actual Paras Arts data.

WRITE OPERATIONS:

The following operations are allowed:

- Update order status
- Update payment status
- Update artwork featured status
- Update service price
- Update FAQ answer

A write operation MUST NOT be executed until the Python
application gets explicit confirmation from the user.

RESPONSE STYLE:

- Be concise.
- Use headings when useful.
- Use bullet points for lists.
- Use small tables when appropriate.
- Clearly distinguish database facts from calculations.
- Give direct answers to simple questions.
- Do not expose unnecessary customer information.
"""


# ============================================================
# RETRY DETECTION
# ============================================================

def is_retryable_gemini_error(error):
    """
    Check whether a Gemini error is temporary and
    suitable for retry/fallback.
    """

    error_text = str(error).lower()

    retry_markers = [
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
    ]

    return any(
        marker in error_text
        for marker in retry_markers
    )


# ============================================================
# GEMINI CALL WITH FALLBACK
# ============================================================

def generate_with_fallback(contents):
    """
    Try Gemini models in order.

    Primary:
        gemini-3.8-flash

    Fallback:
        gemini-3.7-flash
        gemini-3.6-flash
    """

    last_error = None

    for model_index, model in enumerate(MODELS):

        for retry_number in range(
            MAX_RETRIES_PER_MODEL + 1
        ):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        tools=[tools],
                        automatic_function_calling=(
                            types.AutomaticFunctionCallingConfig(
                                disable=True
                            )
                        ),
                        temperature=0.2,
                        max_output_tokens=800,
                    ),
                )

                if model_index > 0:

                    print(
                        f"\n✅ Fallback successful: {model}"
                    )

                return response

            except Exception as error:

                last_error = error

                if not is_retryable_gemini_error(error):
                    raise

                # Retry current model once
                if retry_number < MAX_RETRIES_PER_MODEL:

                    delay = (
                        1.0 +
                        random.uniform(0.1, 0.5)
                    )

                    print(
                        f"\n⚠️ {model} temporarily unavailable."
                        f" Retrying in {delay:.1f}s..."
                    )

                    time.sleep(delay)

                else:

                    # Move to next model
                    if model_index < len(MODELS) - 1:

                        next_model = MODELS[
                            model_index + 1
                        ]

                        print(
                            f"\n⚠️ {model} unavailable."
                            f" Switching to {next_model}..."
                        )

                    else:

                        print(
                            "\n❌ All Gemini models are "
                            "currently unavailable."
                        )

    if last_error:
        raise last_error

    raise RuntimeError(
        "Gemini request failed without a specific error."
    )


# ============================================================
# CONFIRMATION HELPERS
# ============================================================

def get_order_for_confirmation(order_id):

    return db.orders.find_one(
        {"orderId": order_id},
        {
            "_id": 1,
            "orderId": 1,
            "fullName": 1,
            "sketchType": 1,
            "paperSize": 1,
            "status": 1,
            "paymentStatus": 1,
        },
    )


def get_artwork_for_confirmation(title):

    return db.artworks.find_one(
        {"title": title},
        {
            "_id": 1,
            "title": 1,
            "category": 1,
            "featured": 1,
        },
    )


def get_service_for_confirmation(title):

    return db.services.find_one(
        {"title": title},
        {
            "_id": 1,
            "title": 1,
            "priceFrom": 1,
        },
    )


def get_faq_for_confirmation(question):

    return db.faqs.find_one(
        {"question": question},
        {
            "_id": 1,
            "question": 1,
            "answer": 1,
        },
    )


# ============================================================
# WRITE CONFIRMATION
# ============================================================

def ask_for_confirmation(function_name, args):

    print("\n" + "=" * 55)
    print("WRITE OPERATION REQUIRES CONFIRMATION")
    print("=" * 55)

    if function_name == "update_paras_order_status":

        order_id = args["order_id"]
        new_status = args["new_status"]

        order = get_order_for_confirmation(order_id)

        if not order:
            print(
                f"Order '{order_id}' was not found."
            )
            return False

        print(
            f"Order ID: {order.get('orderId')}"
        )
        print(
            f"Customer: {order.get('fullName')}"
        )
        print(
            f"Current status: {order.get('status')}"
        )
        print(
            f"New status: {new_status}"
        )

    elif function_name == "update_paras_payment_status":

        order_id = args["order_id"]
        new_status = args["new_payment_status"]

        order = get_order_for_confirmation(order_id)

        if not order:
            print(
                f"Order '{order_id}' was not found."
            )
            return False

        print(
            f"Order ID: {order.get('orderId')}"
        )
        print(
            f"Current payment status: "
            f"{order.get('paymentStatus')}"
        )
        print(
            f"New payment status: {new_status}"
        )

    elif function_name == "update_paras_artwork_featured":

        title = args["title"]
        featured = args["featured"]

        artwork = get_artwork_for_confirmation(title)

        if not artwork:
            print(
                f"Artwork '{title}' was not found."
            )
            return False

        print(
            f"Artwork: {artwork.get('title')}"
        )
        print(
            f"Current featured: "
            f"{artwork.get('featured')}"
        )
        print(
            f"New featured: {featured}"
        )

    elif function_name == "update_paras_service_price":

        title = args["title"]
        new_price = args["new_price"]

        service = get_service_for_confirmation(title)

        if not service:
            print(
                f"Service '{title}' was not found."
            )
            return False

        print(
            f"Service: {service.get('title')}"
        )
        print(
            f"Current price: ₹{service.get('priceFrom')}"
        )
        print(
            f"New price: ₹{new_price}"
        )

    elif function_name == "update_paras_faq_answer":

        question = args["question"]
        new_answer = args["new_answer"]

        faq = get_faq_for_confirmation(question)

        if not faq:
            print(
                f"FAQ '{question}' was not found."
            )
            return False

        print(
            f"Question: {faq.get('question')}"
        )
        print(
            f"Current answer: {faq.get('answer')}"
        )
        print(
            f"New answer: {new_answer}"
        )

    else:

        return False

    print("=" * 55)

    confirmation = input(
        "Type YES to confirm or NO to cancel: "
    ).strip().lower()

    return confirmation in {
        "yes",
        "y",
        "confirm",
        "confirmed",
    }


# ============================================================
# AGENT LOOP
# ============================================================

def run_agent(user_prompt):

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

    MAX_ITERATIONS = 4

    for _ in range(MAX_ITERATIONS):

        response = generate_with_fallback(
            contents
        )

        # ----------------------------------------------------
        # NORMAL RESPONSE
        # ----------------------------------------------------

        if not response.function_calls:

            return response.text

        # ----------------------------------------------------
        # ADD GEMINI RESPONSE
        # ----------------------------------------------------

        if response.candidates:

            contents.append(
                response.candidates[0].content
            )

        # ----------------------------------------------------
        # PROCESS FUNCTION CALLS
        # ----------------------------------------------------

        tool_responses = []

        for function_call in response.function_calls:

            function_name = function_call.name

            args = dict(
                function_call.args or {}
            )

            # ------------------------------------------------
            # UNKNOWN TOOL
            # ------------------------------------------------

            if function_name not in available_functions:

                tool_responses.append(
                    types.Part.from_function_response(
                        name=function_name,
                        response={
                            "error": (
                                f"Unknown function: "
                                f"{function_name}"
                            )
                        },
                    )
                )

                continue

            # ------------------------------------------------
            # WRITE TOOL
            # ------------------------------------------------

            if function_name in WRITE_TOOLS:

                confirmed = ask_for_confirmation(
                    function_name,
                    args
                )

                if not confirmed:

                    result = {
                        "success": False,
                        "message": (
                            "Write operation was "
                            "cancelled by the user."
                        ),
                    }

                else:

                    try:

                        result = available_functions[
                            function_name
                        ](**args)

                    except Exception as error:

                        result = {
                            "success": False,
                            "error": str(error),
                        }

                tool_responses.append(
                    types.Part.from_function_response(
                        name=function_name,
                        response={
                            "result": result
                        },
                    )
                )

            # ------------------------------------------------
            # READ TOOL
            # ------------------------------------------------

            else:

                try:

                    result = available_functions[
                        function_name
                    ](**args)

                except Exception as error:

                    result = {
                        "success": False,
                        "error": str(error),
                    }

                tool_responses.append(
                    types.Part.from_function_response(
                        name=function_name,
                        response={
                            "result": result
                        },
                    )
                )

        # ----------------------------------------------------
        # SEND TOOL RESULTS BACK TO GEMINI
        # ----------------------------------------------------

        contents.append(
            types.Content(
                role="user",
                parts=tool_responses,
            )
        )

    return (
        "I couldn't complete the analysis within "
        "the allowed number of steps."
    )


# ============================================================
# CLI
# ============================================================

def main():

    print("=" * 38)
    print(" Paras Arts AI Data Agent")
    print("=" * 38)

    print("MongoDB: test")
    print(
        f"Gemini Models: {', '.join(MODELS)}"
    )

    print(
        "\nAI Data Analyst + Data Management Agent"
    )
    print("Type 'exit' to quit.")

    print("=" * 38)

    while True:

        try:

            user_prompt = input(
                "\nYou: "
            ).strip()

        except KeyboardInterrupt:

            print("\n\nAgent stopped.")
            break

        except EOFError:

            print("\n\nAgent stopped.")
            break

        if not user_prompt:
            continue

        if user_prompt.lower() in {
            "exit",
            "quit",
        }:

            print("\nAgent stopped.")
            break

        try:

            answer = run_agent(
                user_prompt
            )

            print("\nAgent:")
            print(answer)

        except Exception as error:

            print("\n❌ Error:")
            print(error)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()