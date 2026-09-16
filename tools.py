import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is not set in .env")

client = MongoClient(MONGO_URI)

db = client["test"]

customers = db["customers"]


def search_customers(city: str | None = None):
    """
    Search customers by city.

    Args:
        city: City to search for. If omitted, all customers are returned.

    Returns:
        A list of matching customers.
    """

    query = {}

    if city:
        query["city"] = city

    results = list(
        customers.find(
            query,
            {
                "_id": 0,
                "customer_id": 1,
                "name": 1,
                "city": 1,
                "email": 1
            }
        )
    )

    return results


def search_orders(status: str | None = None):
    """
    Search orders by status.

    Args:
        status: Order status such as Pending, Completed, or In Progress.
               If omitted, all orders are returned.

    Returns:
        A list of matching orders.
    """
    query = {}

    if status:
        query["status"] = status

    results = list(
        db["orders"].find(
            query,
            {
                "_id": 0,
                "order_id": 1,
                "customer_id": 1,
                "product_id": 1,
                "quantity": 1,
                "status": 1
            }
        )
    )

    return results

def search_products(category: str | None = None):
    """
    Search products by category.

    Args:
        category: Product category such as Electronics or Accessories.
                   If omitted, all products are returned.

    Returns:
        A list of matching products.
    """
    query = {}

    if category:
        query["category"] = category

    results = list(
        db["products"].find(
            query,
            {
                "_id": 0,
                "product_id": 1,
                "name": 1,
                "category": 1,
                "price": 1
            }
        )
    )

    return results

def analyze_orders():
    """
    Analyze orders by status.

    Returns:
        Total number of orders, total quantity ordered,
        and order counts grouped by status.
    """

    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "order_count": {"$sum": 1},
                "total_quantity": {"$sum": "$quantity"}
            }
        }
    ]

    status_results = list(db["orders"].aggregate(pipeline))

    total_orders = db["orders"].count_documents({})

    total_quantity = sum(
        item["total_quantity"]
        for item in status_results
    )

    return {
        "total_orders": total_orders,
        "total_quantity": total_quantity,
        "by_status": status_results
    }

def search_paras_orders(status: str | None = None):
    """
    Search real Paras Arts orders by order status.

    Args:
        status: Order status such as Pending, Accepted,
                In Progress, Completed, or Cancelled.
                If omitted, all orders are returned.

    Returns:
        A list of relevant order information.
    """

    query = {}

    if status:
        query["status"] = status

    results = list(
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
                "createdAt": 1
            }
        )
    )

    return results

def analyze_paras_orders():
    """
    Analyze Paras Arts orders by status.

    Returns:
        Total orders and order counts grouped by status.
    """

    pipeline = [
        {
            "$group": {
                "_id": "$status",
                "order_count": {"$sum": 1}
            }
        }
    ]

    status_results = list(
        db["orders"].aggregate(pipeline)
    )

    total_orders = db["orders"].count_documents({})

    return {
        "total_orders": total_orders,
        "by_status": status_results
    }


if __name__ == "__main__":
    print("Paras Arts Order Analysis:")
    print(analyze_paras_orders())
