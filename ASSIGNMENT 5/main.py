from fastapi import FastAPI, HTTPException, Query

app = FastAPI()

# Sample Data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics"},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery"},
]

orders = []
order_counter = 1


# -------------------------------
# Q4 — SEARCH ORDERS
# -------------------------------
@app.get("/orders/search")
def search_orders(customer_name: str = Query(...)):
    result = [
        order for order in orders
        if customer_name.lower() in order["customer_name"].lower()
    ]

    if not result:
        return {"message": f"No orders found for: {customer_name}"}

    return {
        "customer_name": customer_name,
        "total_found": len(result),
        "orders": result
    }


# -------------------------------
# POST ORDER (for testing Q4 & Bonus)
# -------------------------------
@app.post("/orders")
def create_order(customer_name: str):
    global order_counter

    order = {
        "order_id": order_counter,
        "customer_name": customer_name
    }

    orders.append(order)
    order_counter += 1

    return {"message": "Order placed successfully", "order": order}


# -------------------------------
# Q5 — SORT BY CATEGORY + PRICE
# -------------------------------
@app.get("/products/sort-by-category")
def sort_by_category():
    sorted_products = sorted(
        products,
        key=lambda x: (x["category"], x["price"])
    )

    return sorted_products


# -------------------------------
# Q6 — BROWSE (SEARCH + SORT + PAGINATION)
# -------------------------------
@app.get("/products/browse")
def browse_products(
    keyword: str = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    result = products

    # 🔍 Search
    if keyword:
        result = [
            p for p in result
            if keyword.lower() in p["name"].lower()
        ]

    # ↕ Sort
    if sort_by not in ["price", "name"]:
        raise HTTPException(status_code=400, detail="sort_by must be 'price' or 'name'")

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    # 📄 Pagination
    total_found = len(result)
    start = (page - 1) * limit
    end = start + limit

    paginated = result[start:end]

    total_pages = (total_found + limit - 1) // limit

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total_found": total_found,
        "total_pages": total_pages,
        "products": paginated
    }


# -------------------------------
# ⭐ BONUS — PAGINATE ORDERS
# -------------------------------
@app.get("/orders/page")
def paginate_orders(page: int = 1, limit: int = 3):
    total = len(orders)

    start = (page - 1) * limit
    end = start + limit

    paginated = orders[start:end]

    total_pages = (total + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total_orders": total,
        "total_pages": total_pages,
        "orders": paginated
    }