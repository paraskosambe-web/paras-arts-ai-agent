import os
import re
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in .env")


# ============================================================
# MONGODB
# ============================================================

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
    socketTimeoutMS=20000,
)

# REAL PARAS ARTS DATABASE
db = client["test"]


# ============================================================
# CONFIGURATION
# ============================================================

# Prevent very large MongoDB results from being sent to Gemini.
MAX_SEARCH_RESULTS = 50


# ============================================================
# HELPERS
# ============================================================

def serialize_value(value: Any):
    """
    Convert MongoDB/Python values into JSON-safe values.
    """

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            key: serialize_value(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [
            serialize_value(item)
            for item in value
        ]

    return value


def serialize_documents(documents: list[dict]):
    """
    Convert MongoDB documents into JSON-safe dictionaries.
    """

    return [
        serialize_value(document)
        for document in documents
    ]


def safe_regex_pattern(value: str):
    """
    Escape user-provided search text before using it in MongoDB regex.

    This prevents special regex characters from unexpectedly changing
    the search behavior.
    """

    return re.escape(value.strip())


# ============================================================
# LEVEL 2 — READ / ANALYSIS TOOLS
# ============================================================


def search_paras_orders(
    status: str | None = None,
):
    """
    Search Paras Arts orders.

    Only safe business fields are returned.
    Sensitive customer information such as email, phone,
    address and reference image URLs is intentionally excluded.
    """

    query = {}

    if status:
        query["status"] = status.strip()

    documents = list(
        db["orders"]
        .find(
            query,
            {
                "_id": 0,
                "orderId": 1,
                "fullName": 1,
                "sketchType": 1,
                "paperSize": 1,
                "budget": 1,
                "paymentStatus": 1,
                "status": 1,
                "preferredDate": 1,
                "createdAt": 1,
            },
        )
        .sort("createdAt", -1)
        .limit(MAX_SEARCH_RESULTS)
    )

    return {
        "count_returned": len(documents),
        "limit": MAX_SEARCH_RESULTS,
        "orders": serialize_documents(documents),
    }


def analyze_paras_orders():
    """
    Analyze orders by order status.
    """

    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "order_count": {"$sum": 1},
            }
        },
        {
            "$sort": {
                "order_count": -1,
            }
        },
    ]

    results = list(
        db["orders"].aggregate(pipeline)
    )

    return serialize_value({
        "total_orders": db["orders"].count_documents({}),
        "by_status": results,
    })


def analyze_paras_payments():
    """
    Analyze orders by payment status.
    """

    pipeline = [
        {
            "$group": {
                "_id": "$paymentStatus",
                "order_count": {"$sum": 1},
            }
        },
        {
            "$sort": {
                "order_count": -1,
            }
        },
    ]

    results = list(
        db["orders"].aggregate(pipeline)
    )

    return serialize_value({
        "total_orders": db["orders"].count_documents({}),
        "by_payment_status": results,
    })


def analyze_paras_sketch_types():
    """
    Analyze orders by sketch type.
    """

    pipeline = [
        {
            "$group": {
                "_id": "$sketchType",
                "order_count": {"$sum": 1},
            }
        },
        {
            "$sort": {
                "order_count": -1,
            }
        },
    ]

    return serialize_value({
        "by_sketch_type": list(
            db["orders"].aggregate(pipeline)
        )
    })


def analyze_paras_budgets():
    """
    Analyze requested order budgets.

    These values are NOT revenue.
    """

    pipeline = [
        {
            "$match": {
                "budget": {
                    "$type": "number"
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "order_count": {
                    "$sum": 1
                },
                "average_budget": {
                    "$avg": "$budget"
                },
                "minimum_budget": {
                    "$min": "$budget"
                },
                "maximum_budget": {
                    "$max": "$budget"
                },
                "total_requested_budget": {
                    "$sum": "$budget"
                },
            }
        },
    ]

    results = list(
        db["orders"].aggregate(pipeline)
    )

    if not results:
        return {
            "order_count": 0,
            "average_budget": 0,
            "minimum_budget": 0,
            "maximum_budget": 0,
            "total_requested_budget": 0,
        }

    result = results[0]

    result.pop("_id", None)

    return serialize_value(result)


# ============================================================
# ARTWORKS
# ============================================================


def search_paras_artworks(
    category: str | None = None,
    featured: bool | None = None,
):
    """
    Search Paras Arts artworks.
    """

    query = {}

    if category:
        query["category"] = category.strip()

    if featured is not None:
        query["featured"] = featured

    documents = list(
        db["artworks"]
        .find(
            query,
            {
                "_id": 0,
                "title": 1,
                "category": 1,
                "medium": 1,
                "paperSize": 1,
                "description": 1,
                "price": 1,
                "featured": 1,
                "createdAt": 1,
            },
        )
        .sort("createdAt", -1)
        .limit(MAX_SEARCH_RESULTS)
    )

    return {
        "count_returned": len(documents),
        "limit": MAX_SEARCH_RESULTS,
        "artworks": serialize_documents(documents),
    }


def analyze_paras_artworks():
    """
    Analyze artwork categories and featured artworks.
    """

    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "artwork_count": {
                    "$sum": 1
                },
            }
        },
        {
            "$sort": {
                "artwork_count": -1,
            }
        },
    ]

    return serialize_value({
        "total_artworks": db["artworks"].count_documents({}),

        "featured_artworks": db["artworks"].count_documents(
            {
                "featured": True
            }
        ),

        "by_category": list(
            db["artworks"].aggregate(pipeline)
        ),
    })


# ============================================================
# SERVICES
# ============================================================


def search_paras_services(
    title: str | None = None,
):
    """
    Search Paras Arts services.

    If a title is provided, it performs a case-insensitive
    partial title search instead of requiring an exact match.
    """

    query = {}

    if title and title.strip():

        search_text = safe_regex_pattern(title)

        query["title"] = {
            "$regex": search_text,
            "$options": "i",
        }

    documents = list(
        db["services"]
        .find(
            query,
            {
                "_id": 0,
                "title": 1,
                "description": 1,
                "priceFrom": 1,
                "delivery": 1,
                "createdAt": 1,
            },
        )
        .sort("createdAt", -1)
        .limit(MAX_SEARCH_RESULTS)
    )

    return {
        "count_returned": len(documents),
        "limit": MAX_SEARCH_RESULTS,
        "services": serialize_documents(documents),
    }


def analyze_paras_services():
    """
    Analyze Paras Arts services and pricing.
    """

    documents = list(
        db["services"].find(
            {},
            {
                "_id": 0,
                "title": 1,
                "priceFrom": 1,
                "delivery": 1,
            },
        )
    )

    return serialize_value({
        "total_services": len(documents),
        "services": documents,
    })


# ============================================================
# FAQS
# ============================================================


def search_paras_faqs(
    category: str | None = None,
    keyword: str | None = None,
):
    """
    Search Paras Arts FAQs.

    Supports optional category and keyword filtering.
    Keyword search checks both question and answer.
    """

    query = {}

    if category and category.strip():

        query["category"] = category.strip()

    if keyword and keyword.strip():

        safe_keyword = safe_regex_pattern(keyword)

        query["$or"] = [
            {
                "question": {
                    "$regex": safe_keyword,
                    "$options": "i",
                }
            },
            {
                "answer": {
                    "$regex": safe_keyword,
                    "$options": "i",
                }
            },
        ]

    documents = list(
        db["faqs"]
        .find(
            query,
            {
                "_id": 0,
                "question": 1,
                "answer": 1,
                "category": 1,
                "createdAt": 1,
            },
        )
        .sort("createdAt", -1)
        .limit(MAX_SEARCH_RESULTS)
    )

    return {
        "count_returned": len(documents),
        "limit": MAX_SEARCH_RESULTS,
        "faqs": serialize_documents(documents),
    }


def analyze_paras_faqs():
    """
    Analyze FAQ categories.
    """

    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "faq_count": {
                    "$sum": 1
                },
            }
        },
        {
            "$sort": {
                "faq_count": -1,
            }
        },
    ]

    return serialize_value({
        "total_faqs": db["faqs"].count_documents({}),
        "by_category": list(
            db["faqs"].aggregate(pipeline)
        ),
    })


# ============================================================
# BUSINESS SUMMARY
# ============================================================


def get_paras_business_summary():
    """
    Overall read-only Paras Arts database summary.

    The admins collection is intentionally excluded.
    """

    order_status = list(
        db["orders"].aggregate(
            [
                {
                    "$group": {
                        "_id": "$status",
                        "count": {
                            "$sum": 1
                        },
                    }
                },
                {
                    "$sort": {
                        "count": -1,
                    }
                },
            ]
        )
    )

    payment_status = list(
        db["orders"].aggregate(
            [
                {
                    "$group": {
                        "_id": "$paymentStatus",
                        "count": {
                            "$sum": 1
                        },
                    }
                },
                {
                    "$sort": {
                        "count": -1,
                    }
                },
            ]
        )
    )

    return serialize_value({
        "orders": db["orders"].count_documents({}),

        "artworks": db["artworks"].count_documents({}),

        "services": db["services"].count_documents({}),

        "faqs": db["faqs"].count_documents({}),

        "testimonials": db["testimonials"].count_documents({}),

        "messages": db["messages"].count_documents({}),

        "newsletter_subscribers": (
            db["newsletters"].count_documents({})
        ),

        "orders_by_status": order_status,

        "orders_by_payment_status": payment_status,
    })


# ============================================================
# LEVEL 3 — WRITE TOOLS
# ============================================================

# IMPORTANT:
#
# These functions DO NOT ask for confirmation themselves.
#
# Confirmation is handled by api.py BEFORE these functions
# are executed.
#
# These functions still perform their own validation as a
# second security layer.
# ============================================================


ALLOWED_ORDER_STATUSES = {
    "Pending",
    "Accepted",
    "In Progress",
    "Completed",
    "Cancelled",
}


ALLOWED_PAYMENT_STATUSES = {
    "Pending",
    "Verified",
    "Failed",
}


# ============================================================
# UPDATE ORDER STATUS
# ============================================================


def update_paras_order_status(
    order_id: str,
    new_status: str,
):
    """
    Update the status of one Paras Arts order.
    """

    if not order_id or not order_id.strip():
        return {
            "success": False,
            "error": "Order ID is required.",
        }

    if new_status not in ALLOWED_ORDER_STATUSES:
        return {
            "success": False,
            "error": (
                f"Invalid order status: {new_status}. "
                f"Allowed values: "
                f"{', '.join(sorted(ALLOWED_ORDER_STATUSES))}."
            ),
        }

    order_id = order_id.strip()

    order = db["orders"].find_one(
        {
            "orderId": order_id
        },
        {
            "_id": 0,
            "orderId": 1,
            "status": 1,
        },
    )

    if not order:
        return {
            "success": False,
            "error": (
                f"Order {order_id} was not found."
            ),
        }

    old_status = order.get("status")

    if old_status == new_status:
        return {
            "success": True,
            "changed": False,
            "orderId": order_id,
            "old_status": old_status,
            "new_status": new_status,
            "message": "Order already has this status.",
        }

    result = db["orders"].update_one(
        {
            "orderId": order_id,
            "status": old_status,
        },
        {
            "$set": {
                "status": new_status
            }
        },
    )

    if result.modified_count == 1:
        return {
            "success": True,
            "changed": True,
            "orderId": order_id,
            "old_status": old_status,
            "new_status": new_status,
            "message": (
                f"Order {order_id} status changed "
                f"from {old_status} to {new_status}."
            ),
        }

    return {
        "success": False,
        "error": (
            "MongoDB update did not modify the order. "
            "The order may have changed before confirmation."
        ),
    }


# ============================================================
# UPDATE PAYMENT STATUS
# ============================================================


def update_paras_payment_status(
    order_id: str,
    new_payment_status: str,
):
    """
    Update payment status for one Paras Arts order.
    """

    if not order_id or not order_id.strip():
        return {
            "success": False,
            "error": "Order ID is required.",
        }

    if new_payment_status not in ALLOWED_PAYMENT_STATUSES:
        return {
            "success": False,
            "error": (
                f"Invalid payment status: "
                f"{new_payment_status}. "
                f"Allowed values: "
                f"{', '.join(sorted(ALLOWED_PAYMENT_STATUSES))}."
            ),
        }

    order_id = order_id.strip()

    order = db["orders"].find_one(
        {
            "orderId": order_id
        },
        {
            "_id": 0,
            "orderId": 1,
            "paymentStatus": 1,
        },
    )

    if not order:
        return {
            "success": False,
            "error": (
                f"Order {order_id} was not found."
            ),
        }

    old_status = order.get("paymentStatus")

    if old_status == new_payment_status:
        return {
            "success": True,
            "changed": False,
            "orderId": order_id,
            "old_payment_status": old_status,
            "new_payment_status": new_payment_status,
            "message": (
                "Payment already has this status."
            ),
        }

    result = db["orders"].update_one(
        {
            "orderId": order_id,
            "paymentStatus": old_status,
        },
        {
            "$set": {
                "paymentStatus": new_payment_status
            }
        },
    )

    if result.modified_count == 1:
        return {
            "success": True,
            "changed": True,
            "orderId": order_id,
            "old_payment_status": old_status,
            "new_payment_status": new_payment_status,
            "message": (
                f"Payment status for order {order_id} "
                f"changed from {old_status} "
                f"to {new_payment_status}."
            ),
        }

    return {
        "success": False,
        "error": (
            "MongoDB update did not modify the payment status. "
            "The order may have changed before confirmation."
        ),
    }


# ============================================================
# UPDATE ARTWORK FEATURED STATUS
# ============================================================


def update_paras_artwork_featured(
    title: str,
    featured: bool,
):
    """
    Change the featured status of one artwork.
    """

    if not title or not title.strip():
        return {
            "success": False,
            "error": "Artwork title is required.",
        }

    title = title.strip()

    artwork = db["artworks"].find_one(
        {
            "title": title
        },
        {
            "_id": 0,
            "title": 1,
            "featured": 1,
        },
    )

    if not artwork:
        return {
            "success": False,
            "error": (
                f"Artwork '{title}' was not found."
            ),
        }

    old_value = artwork.get("featured")

    if old_value == featured:
        return {
            "success": True,
            "changed": False,
            "title": title,
            "old_featured": old_value,
            "new_featured": featured,
            "message": (
                "Artwork already has this featured status."
            ),
        }

    result = db["artworks"].update_one(
        {
            "title": title,
            "featured": old_value,
        },
        {
            "$set": {
                "featured": featured
            }
        },
    )

    if result.modified_count == 1:
        return {
            "success": True,
            "changed": True,
            "title": title,
            "old_featured": old_value,
            "new_featured": featured,
            "message": (
                f"Artwork '{title}' featured status "
                f"changed to {featured}."
            ),
        }

    return {
        "success": False,
        "error": (
            "MongoDB update did not modify the artwork. "
            "The artwork may have changed before confirmation."
        ),
    }


# ============================================================
# UPDATE SERVICE PRICE
# ============================================================


def update_paras_service_price(
    title: str,
    new_price: float,
):
    """
    Update the starting price of one service.
    """

    if not title or not title.strip():
        return {
            "success": False,
            "error": "Service title is required.",
        }

    try:
        new_price = float(new_price)
    except (TypeError, ValueError):
        return {
            "success": False,
            "error": "Service price must be a valid number.",
        }

    if new_price < 0:
        return {
            "success": False,
            "error": "Price cannot be negative.",
        }

    title = title.strip()

    service = db["services"].find_one(
        {
            "title": title
        },
        {
            "_id": 0,
            "title": 1,
            "priceFrom": 1,
        },
    )

    if not service:
        return {
            "success": False,
            "error": (
                f"Service '{title}' was not found."
            ),
        }

    old_price = service.get("priceFrom")

    if old_price == new_price:
        return {
            "success": True,
            "changed": False,
            "title": title,
            "old_price": old_price,
            "new_price": new_price,
            "message": (
                "Service already has this price."
            ),
        }

    result = db["services"].update_one(
        {
            "title": title,
            "priceFrom": old_price,
        },
        {
            "$set": {
                "priceFrom": new_price
            }
        },
    )

    if result.modified_count == 1:
        return {
            "success": True,
            "changed": True,
            "title": title,
            "old_price": old_price,
            "new_price": new_price,
            "message": (
                f"Service '{title}' price changed "
                f"from ₹{old_price} to ₹{new_price}."
            ),
        }

    return {
        "success": False,
        "error": (
            "MongoDB update did not modify the service. "
            "The service may have changed before confirmation."
        ),
    }


# ============================================================
# UPDATE FAQ ANSWER
# ============================================================


def update_paras_faq_answer(
    question: str,
    new_answer: str,
):
    """
    Update the answer of one FAQ identified by its question.
    """

    if not question or not question.strip():
        return {
            "success": False,
            "error": "FAQ question is required.",
        }

    if not new_answer or not new_answer.strip():
        return {
            "success": False,
            "error": "FAQ answer cannot be empty.",
        }

    question = question.strip()
    new_answer = new_answer.strip()

    faq = db["faqs"].find_one(
        {
            "question": question
        },
        {
            "_id": 0,
            "question": 1,
            "answer": 1,
        },
    )

    if not faq:
        return {
            "success": False,
            "error": (
                "FAQ with that question was not found."
            ),
        }

    old_answer = faq.get("answer")

    if old_answer == new_answer:
        return {
            "success": True,
            "changed": False,
            "question": question,
            "message": (
                "FAQ answer is already the same."
            ),
        }

    result = db["faqs"].update_one(
        {
            "question": question,
            "answer": old_answer,
        },
        {
            "$set": {
                "answer": new_answer
            }
        },
    )

    if result.modified_count == 1:
        return {
            "success": True,
            "changed": True,
            "question": question,
            "message": (
                "FAQ answer updated successfully."
            ),
        }

    return {
        "success": False,
        "error": (
            "MongoDB update did not modify the FAQ. "
            "The FAQ may have changed before confirmation."
        ),
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("\n======================================")
    print(" Paras Arts MongoDB Tools")
    print("======================================")

    try:

        # Test MongoDB connection
        client.admin.command("ping")

        print("\nMongoDB connection: OK")

        print("\nDatabase:")
        print(db.name)

        print("\nBusiness Summary:")
        print(get_paras_business_summary())

        print("\nBudget Analysis:")
        print(analyze_paras_budgets())

        print("\nSketch Type Analysis:")
        print(analyze_paras_sketch_types())

        print("\nArtwork Analysis:")
        print(analyze_paras_artworks())

        print("\nService Analysis:")
        print(analyze_paras_services())

        print("\nFAQ Analysis:")
        print(analyze_paras_faqs())

        print("\nWrite tools loaded successfully.")
        print("No write operation was executed.")

    except Exception as error:

        print(
            f"\nMongoDB/tool error: "
            f"{type(error).__name__}: {error}"
        )