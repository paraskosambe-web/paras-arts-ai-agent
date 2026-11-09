import os
import re
from datetime import datetime, timedelta, timezone
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
db = client[os.getenv("MONGO_DB_NAME", "test")]


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


def build_chart(title: str, records: list[dict], value_key: str, chart_type="bar", currency=None):
    """Build a compact chart payload from grouped MongoDB results."""
    return {
        "type": chart_type,
        "title": title,
        "value_label": value_key.replace("_", " ").title(),
        "currency": currency,
        "data": [
            {"label": str(row.get("_id") or "Unknown"), "value": row.get(value_key, 0) or 0}
            for row in records
        ],
    }


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
        "visualization": build_chart("Orders by Status", results, "order_count", "donut"),
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
        "visualization": build_chart("Payment Status", results, "order_count", "donut"),
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

    results = list(db["orders"].aggregate(pipeline))
    return serialize_value({
        "by_sketch_type": results,
        "visualization": build_chart("Orders by Sketch Type", results, "order_count"),
    })


def analyze_paras_order_trends(period: str = "month", periods: int = 8):
    """Aggregate orders with valid createdAt dates into a bounded timeline."""
    period = (period or "month").lower()
    if period not in {"day", "week", "month"}:
        period = "month"
    try:
        periods = max(2, min(int(periods), 24))
    except (TypeError, ValueError):
        periods = 8

    now = datetime.now(timezone.utc)
    if period == "month":
        month_index = now.year * 12 + now.month - 1 - (periods - 1)
        year, month_zero_based = divmod(month_index, 12)
        start = datetime(year, month_zero_based + 1, 1, tzinfo=timezone.utc)
    elif period == "week":
        current_week = now.replace(hour=0, minute=0, second=0, microsecond=0)
        current_week -= timedelta(days=current_week.weekday())
        start = current_week - timedelta(weeks=periods - 1)
    else:
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start = today - timedelta(days=periods - 1)
    date_format = {"day": "%Y-%m-%d", "week": "%G-W%V", "month": "%Y-%m"}[period]
    period_name = {"day": "Daily", "week": "Weekly", "month": "Monthly"}[period]
    results = list(db["orders"].aggregate([
        {"$match": {"createdAt": {"$gte": start, "$type": "date"}}},
        {"$group": {
            "_id": {"$dateToString": {"format": date_format, "date": "$createdAt", "timezone": "UTC"}},
            "order_count": {"$sum": 1},
        }},
        {"$sort": {"_id": 1}},
    ]))
    return serialize_value({
        "period": period,
        "periods_requested": periods,
        "orders_in_window": sum(row["order_count"] for row in results),
        "trend": results,
        "visualization": {
            **build_chart(f"Orders Over Time ({period_name})", results, "order_count", "line"),
            "value_label": "Orders",
        },
        "note": "Only records with a MongoDB date in createdAt are included.",
    })


def analyze_paras_order_segments(dimension: str = "sketchType", metric: str = "count"):
    """Compare orders across approved fields using count or average requested budget."""
    dimensions = {
        "status": "$status",
        "paymentStatus": "$paymentStatus",
        "sketchType": "$sketchType",
    }
    if dimension not in dimensions:
        dimension = "sketchType"
    if metric not in {"count", "average_budget"}:
        metric = "count"

    group = {"_id": dimensions[dimension]}
    if metric == "count":
        group["value"] = {"$sum": 1}
    else:
        group["value"] = {
            "$avg": {
                "$cond": [
                    {"$isNumber": "$budget"},
                    "$budget",
                    None,
                ]
            }
        }

    results = list(db["orders"].aggregate([
        {"$group": group},
        {"$sort": {"value": -1}},
    ]))
    metric_label = "Average Requested Budget" if metric == "average_budget" else "Orders"
    return serialize_value({
        "dimension": dimension,
        "metric": metric,
        "groups": results,
        "visualization": build_chart(
            f"{metric_label} by {dimension}",
            results,
            "value",
            currency="INR" if metric == "average_budget" else None,
        ),
        "note": "Average requested budget is not revenue." if metric == "average_budget" else None,
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
        result = {
            "order_count": 0,
            "average_budget": 0,
            "minimum_budget": 0,
            "maximum_budget": 0,
            "total_requested_budget": 0,
        }
    else:
        result = results[0]
        result.pop("_id", None)

    result = serialize_value(result)
    result["visualization"] = {
        "type": "bar",
        "title": "Requested Budget Summary",
        "value_label": "Amount",
        "currency": "INR",
        "data": [
            {"label": "Average", "value": result["average_budget"]},
            {"label": "Minimum", "value": result["minimum_budget"]},
            {"label": "Maximum", "value": result["maximum_budget"]},
        ],
    }
    return result


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

    categories = list(db["artworks"].aggregate(pipeline))
    return serialize_value({
        "total_artworks": db["artworks"].count_documents({}),

        "featured_artworks": db["artworks"].count_documents(
            {
                "featured": True
            }
        ),

        "by_category": categories,
        "visualization": build_chart("Artworks by Category", categories, "artwork_count", "donut"),
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

    prices = [
        {"_id": item.get("title", "Service"), "price": item.get("priceFrom", 0)}
        for item in documents
        if isinstance(item.get("priceFrom"), (int, float))
    ]
    return serialize_value({
        "total_services": len(documents),
        "services": documents,
        "visualization": build_chart("Starting Price by Service", prices, "price", currency="INR"),
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

    categories = list(db["faqs"].aggregate(pipeline))
    return serialize_value({
        "total_faqs": db["faqs"].count_documents({}),
        "by_category": categories,
        "visualization": build_chart("FAQs by Category", categories, "faq_count", "donut"),
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
        "visualizations": [
            build_chart("Orders by Status", order_status, "count", "donut"),
            build_chart("Payments by Status", payment_status, "count", "donut"),
        ],
    })


def generate_paras_business_performance_report():
    """Return a bounded, privacy-safe, all-time BI snapshot for a full business report."""
    orders = db["orders"]
    artworks = db["artworks"]
    report_collections = ["orders", "artworks", "services", "messages", "testimonials", "newsletters"]
    available_collections = set(db.list_collection_names(
        filter={"name": {"$in": report_collections}}
    ))

    def collection_count(name):
        return db[name].count_documents({}) if name in available_collections else None

    def grouped_counts(collection, field, count_key="count"):
        return list(collection.aggregate([
            {"$group": {
                "_id": {"$ifNull": [f"${field}", "Unknown"]},
                count_key: {"$sum": 1},
            }},
            {"$sort": {count_key: -1}},
            {"$limit": 30},
        ]))

    orders_available = "orders" in available_collections
    artworks_available = "artworks" in available_collections
    total_orders = collection_count("orders")
    order_status = grouped_counts(orders, "status") if orders_available else None
    payment_status = grouped_counts(orders, "paymentStatus") if orders_available else None
    artwork_categories = grouped_counts(artworks, "category") if artworks_available else None

    service_field = next((
        field for field in ("serviceTitle", "serviceName", "service", "sketchType")
        if orders.find_one({field: {"$type": "string"}}, {"_id": 0, field: 1})
    ), None) if orders_available else None
    order_types = grouped_counts(orders, service_field) if service_field else None
    service_field_is_proxy = service_field == "sketchType"

    order_category_field = next((
        field for field in ("artworkCategory", "artwork_category")
        if orders.find_one({field: {"$type": "string"}}, {"_id": 0, field: 1})
    ), None) if orders_available else None
    orders_by_artwork_category = (
        grouped_counts(orders, order_category_field)
        if order_category_field else None
    )

    message_count = collection_count("messages")
    testimonial_count = collection_count("testimonials")
    newsletter_count = collection_count("newsletters")
    newsletter_status_field = next((
        field for field in ("subscriptionStatus", "status")
        if db["newsletters"].find_one({field: {"$type": "string"}}, {"_id": 0, field: 1})
    ), None) if newsletter_count is not None else None
    if newsletter_status_field is None:
        newsletter_status_field = next((
            field for field in ("isSubscribed", "subscribed")
            if db["newsletters"].find_one({field: {"$type": "bool"}}, {"_id": 0, field: 1})
        ), None) if newsletter_count is not None else None
    newsletter_status = (
        grouped_counts(db["newsletters"], newsletter_status_field)
        if newsletter_status_field else None
    )

    completed_count = orders.count_documents({"status": "Completed"}) if orders_available else None
    amount_field = next((
        field for field in ("paidAmount", "amountPaid", "paymentAmount", "transactionAmount", "amount", "totalAmount")
        if orders.find_one({field: {"$type": "number"}}, {"_id": 0, field: 1})
    ), None) if orders_available else None
    revenue = {
        "status": "unavailable",
        "value": None,
        "currency": "INR",
        "reason": "No reliable paid-amount field was found; requested budgets and service prices are not revenue.",
    }
    if not orders_available:
        revenue["reason"] = "The orders collection is unavailable."
    elif completed_count == 0:
        revenue = {
            "status": "available",
            "value": 0,
            "currency": "INR",
            "basis": "There are no orders marked Completed.",
        }
    elif amount_field:
        verified_completed = orders.count_documents({
            "status": "Completed",
            "paymentStatus": "Verified",
            amount_field: {"$type": "number"},
        })
        if verified_completed == completed_count:
            total_result = list(orders.aggregate([
                {"$match": {
                    "status": "Completed",
                    "paymentStatus": "Verified",
                    amount_field: {"$type": "number"},
                }},
                {"$group": {"_id": None, "total": {"$sum": f"${amount_field}"}}},
            ]))
            revenue = {
                "status": "available",
                "value": total_result[0]["total"] if total_result else 0,
                "currency": "INR",
                "basis": f"Sum of {amount_field} for completed orders with Verified payment status.",
            }
        else:
            revenue["reason"] = (
                "Completed orders do not all have a numeric paid amount and Verified payment status."
            )

    data_quality = {
        "orders_missing_order_id": orders.count_documents({"$or": [{"orderId": {"$exists": False}}, {"orderId": None}, {"orderId": ""}]}),
        "orders_missing_status": orders.count_documents({"$or": [{"status": {"$exists": False}}, {"status": None}, {"status": ""}]}),
        "orders_missing_payment_status": orders.count_documents({"$or": [{"paymentStatus": {"$exists": False}}, {"paymentStatus": None}, {"paymentStatus": ""}]}),
        "completed_orders_without_verified_payment": orders.count_documents({"status": "Completed", "paymentStatus": {"$ne": "Verified"}}),
        "verified_payments_without_completed_order": orders.count_documents({"paymentStatus": "Verified", "status": {"$ne": "Completed"}}),
        "pending_orders_older_than_7_days": orders.count_documents({
            "status": "Pending",
            "createdAt": {"$type": "date", "$lte": datetime.now(timezone.utc) - timedelta(days=7)},
        }),
        "in_progress_orders_older_than_14_days": orders.count_documents({
            "status": "In Progress",
            "createdAt": {"$type": "date", "$lte": datetime.now(timezone.utc) - timedelta(days=14)},
        }),
    } if orders_available else None

    budget_stats = analyze_paras_budgets() if orders_available else None
    if budget_stats is not None:
        budget_stats.pop("visualization", None)
    order_trends = analyze_paras_order_trends("month", 12) if orders_available else None

    engagement_rows = [
        {"_id": label, "count": value}
        for label, value in (("Messages", message_count), ("Testimonials", testimonial_count), ("Newsletter Records", newsletter_count))
        if value is not None
    ]

    visualizations = [
        build_chart("Orders by Status", order_status or [], "count", "donut"),
        build_chart("Payments by Status", payment_status or [], "count", "donut"),
        build_chart("Artworks by Category", artwork_categories or [], "count", "donut"),
        build_chart(
            "Most Requested Order Types" if service_field_is_proxy else "Most Requested Services",
            order_types or [],
            "count",
        ),
        build_chart("Customer Touchpoints", engagement_rows, "count"),
        order_trends["visualization"] if order_trends else build_chart("Monthly Orders", [], "count", "line"),
    ]

    return serialize_value({
        "report_scope": "All-time counts and distributions unless a metric says otherwise. The report uses business collections only and excludes admin/security data.",
        "orders": {
            "total": total_orders,
            "by_status": order_status,
            "by_payment_status": payment_status,
            "monthly_trend_last_12_periods": order_trends["trend"] if order_trends else None,
        },
        "revenue": revenue,
        "requested_order_budgets": budget_stats,
        "artworks": {
            "total": collection_count("artworks"),
            "by_catalog_category": artwork_categories,
            "orders_by_artwork_category": orders_by_artwork_category,
            "order_category_note": (
                "Orders collection unavailable; order category distribution cannot be checked."
                if not orders_available else (
                    "No artwork category field was found on order records; catalog category counts are not order counts."
                    if orders_by_artwork_category is None else None
                )
            ),
        },
        "service_demand": {
            "service_catalog_count": collection_count("services"),
            "most_requested": order_types,
            "source_field": service_field,
            "note": (
                "Orders collection unavailable; service demand cannot be checked."
                if not orders_available else (
                    "Orders have no explicit service field; sketchType is shown as a demand proxy."
                    if service_field_is_proxy else (
                    "No service or order type field was found on order records."
                    if service_field is None else None
                    )
                )
            ),
        },
        "customer_engagement": {
            "message_records": message_count,
            "testimonial_records": testimonial_count,
            "engagement_rate": None,
            "note": (
                "Counts show recorded touchpoints only; no delivery, response, or conversion denominator is available."
                if message_count is not None and testimonial_count is not None else
                "One or more engagement collections are unavailable; rates cannot be calculated."
            ),
        },
        "newsletter": {
            "records": newsletter_count,
            "subscription_status_field": newsletter_status_field,
            "by_status": newsletter_status,
            "note": (
                "Newsletter collection is unavailable."
                if newsletter_count is None else (
                    None if newsletter_status is not None else
                    "Subscription records are counted; no subscription-status field was found."
                )
            ),
        },
        "data_quality_and_bottlenecks": data_quality,
        "visualizations": visualizations,
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
