import os

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

client = MongoClient(MONGO_URI)

# REAL PARAS ARTS DATABASE
db = client["test"]


# ============================================================
# LEVEL 2 — READ / ANALYSIS TOOLS
# ============================================================


def search_paras_orders(status: str | None = None):
    """
    Search Paras Arts orders.
    """

    query = {}

    if status:
        query["status"] = status

    return list(
        db["orders"].find(
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
    )


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

    return {
        "total_orders": db["orders"].count_documents({}),
        "by_status": results,
    }


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

    return {
        "total_orders": db["orders"].count_documents({}),
        "by_payment_status": results,
    }


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

    return {
        "by_sketch_type": list(
            db["orders"].aggregate(pipeline)
        )
    }


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
                "order_count": {"$sum": 1},
                "average_budget": {"$avg": "$budget"},
                "minimum_budget": {"$min": "$budget"},
                "maximum_budget": {"$max": "$budget"},
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

    return result


def search_paras_artworks(
    category: str | None = None,
    featured: bool | None = None,
):
    """
    Search Paras Arts artworks.
    """

    query = {}

    if category:
        query["category"] = category

    if featured is not None:
        query["featured"] = featured

    return list(
        db["artworks"].find(
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
    )


def analyze_paras_artworks():
    """
    Analyze artwork categories.
    """

    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "artwork_count": {"$sum": 1},
            }
        },
        {
            "$sort": {
                "artwork_count": -1,
            }
        },
    ]

    return {
        "total_artworks": db["artworks"].count_documents({}),
        "featured_artworks": db["artworks"].count_documents(
            {"featured": True}
        ),
        "by_category": list(
            db["artworks"].aggregate(pipeline)
        ),
    }


def search_paras_services(
    title: str | None = None,
):
    """
    Search Paras Arts services.
    """

    query = {}

    if title:
        query["title"] = title

    return list(
        db["services"].find(
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
    )


def analyze_paras_services():
    """
    Analyze Paras Arts services.
    """

    return {
        "total_services": db["services"].count_documents({}),
        "services": list(
            db["services"].find(
                {},
                {
                    "_id": 0,
                    "title": 1,
                    "priceFrom": 1,
                    "delivery": 1,
                },
            )
        ),
    }


def search_paras_faqs(
    category: str | None = None,
    keyword: str | None = None,
):
    """
    Search Paras Arts FAQs.
    """

    query = {}

    if category:
        query["category"] = category

    if keyword:
        query["$or"] = [
            {
                "question": {
                    "$regex": keyword,
                    "$options": "i",
                }
            },
            {
                "answer": {
                    "$regex": keyword,
                    "$options": "i",
                }
            },
        ]

    return list(
        db["faqs"].find(
            query,
            {
                "_id": 0,
                "question": 1,
                "answer": 1,
                "category": 1,
                "createdAt": 1,
            },
        )
    )


def analyze_paras_faqs():
    """
    Analyze FAQ categories.
    """

    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "faq_count": {"$sum": 1},
            }
        },
        {
            "$sort": {
                "faq_count": -1,
            }
        },
    ]

    return {
        "total_faqs": db["faqs"].count_documents({}),
        "by_category": list(
            db["faqs"].aggregate(pipeline)
        ),
    }


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
                        "count": {"$sum": 1},
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
                        "count": {"$sum": 1},
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

    return {
        "orders": db["orders"].count_documents({}),
        "artworks": db["artworks"].count_documents({}),
        "services": db["services"].count_documents({}),
        "faqs": db["faqs"].count_documents({}),
        "testimonials": db["testimonials"].count_documents({}),
        "messages": db["messages"].count_documents({}),
        "newsletter_subscribers": db["newsletters"].count_documents({}),
        "orders_by_status": order_status,
        "orders_by_payment_status": payment_status,
    }


# ============================================================
# LEVEL 3 — WRITE TOOLS
# ============================================================

# IMPORTANT:
# These functions DO NOT ask for confirmation themselves.
# The AI agent handles the confirmation before calling them.


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


def update_paras_order_status(
    order_id: str,
    new_status: str,
):
    """
    Update the status of one Paras Arts order.

    Only allowed status values can be used.
    """

    if new_status not in ALLOWED_ORDER_STATUSES:
        return {
            "success": False,
            "error": (
                f"Invalid order status: {new_status}"
            ),
        }

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
            "orderId": order_id
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
        }

    return {
        "success": False,
        "error": "MongoDB update did not modify the order.",
    }


def update_paras_payment_status(
    order_id: str,
    new_payment_status: str,
):
    """
    Update payment status for one Paras Arts order.
    """

    if new_payment_status not in ALLOWED_PAYMENT_STATUSES:
        return {
            "success": False,
            "error": (
                f"Invalid payment status: "
                f"{new_payment_status}"
            ),
        }

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
            "message": "Payment already has this status.",
        }

    result = db["orders"].update_one(
        {
            "orderId": order_id
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
        }

    return {
        "success": False,
        "error": (
            "MongoDB update did not modify the payment status."
        ),
    }


def update_paras_artwork_featured(
    title: str,
    featured: bool,
):
    """
    Change the featured status of an artwork.
    """

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
            "title": title
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
        }

    return {
        "success": False,
        "error": (
            "MongoDB update did not modify the artwork."
        ),
    }


def update_paras_service_price(
    title: str,
    new_price: float,
):
    """
    Update the starting price of a service.
    """

    if new_price < 0:
        return {
            "success": False,
            "error": "Price cannot be negative.",
        }

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
            "title": title
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
        }

    return {
        "success": False,
        "error": (
            "MongoDB update did not modify the service."
        ),
    }


def update_paras_faq_answer(
    question: str,
    new_answer: str,
):
    """
    Update the answer of one FAQ identified by its question.
    """

    if not new_answer.strip():
        return {
            "success": False,
            "error": "FAQ answer cannot be empty.",
        }

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
            "message": "FAQ answer is already the same.",
        }

    result = db["faqs"].update_one(
        {
            "question": question
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
            "old_answer": old_answer,
            "new_answer": new_answer,
        }

    return {
        "success": False,
        "error": (
            "MongoDB update did not modify the FAQ."
        ),
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("\n======================================")
    print(" Paras Arts MongoDB Tools")
    print("======================================")

    print("\nBusiness Summary:")
    print(get_paras_business_summary())

    print("\nBudget Analysis:")
    print(analyze_paras_budgets())

    print("\nSketch Type Analysis:")
    print(analyze_paras_sketch_types())

    print("\nArtwork Analysis:")
    print(analyze_paras_artworks())

    print("\nFAQ Analysis:")
    print(analyze_paras_faqs())

    print("\nWrite tools loaded successfully.")
    print("No write operation was executed.")