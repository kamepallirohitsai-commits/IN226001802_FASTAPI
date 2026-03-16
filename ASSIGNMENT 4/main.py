from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# ------------------------
# Sample Products Database
# ------------------------

products = {
    1: {"name": "Wireless Mouse", "price": 499, "stock": True},
    2: {"name": "Notebook", "price": 99, "stock": True},
    3: {"name": "USB Hub", "price": 299, "stock": False},
    4: {"name": "Pen Set", "price": 49, "stock": True}
}

# ------------------------
# In-Memory Storage
# ------------------------

cart = {}
orders = []
order_id_counter = 1


# ------------------------
# Checkout Model
# ------------------------

class Checkout(BaseModel):
    customer_name: str
    delivery_address: str


# ------------------------
# Add Item to Cart
# ------------------------

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):

    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[product_id]

    if not product["stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    price = product["price"]

    # If product already in cart → update quantity
    if product_id in cart:
        cart[product_id]["quantity"] += quantity
        cart[product_id]["subtotal"] = cart[product_id]["quantity"] * price

        return {
            "message": "Cart updated",
            "cart_item": cart[product_id]
        }

    # Add new product
    cart[product_id] = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": price,
        "subtotal": price * quantity
    }

    return {
        "message": "Added to cart",
        "cart_item": cart[product_id]
    }


# ------------------------
# View Cart
# ------------------------

@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    items = list(cart.values())

    grand_total = sum(item["subtotal"] for item in items)

    return {
        "items": items,
        "item_count": len(items),
        "grand_total": grand_total
    }


# ------------------------
# Remove Item
# ------------------------

@app.delete("/cart/{product_id}")
def remove_item(product_id: int):

    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Item not in cart")

    removed_item = cart.pop(product_id)

    return {
        "message": f"{removed_item['product_name']} removed from cart"
    }


# ------------------------
# Checkout
# ------------------------

@app.post("/cart/checkout")
def checkout(data: Checkout):

    global order_id_counter

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    placed_orders = []
    grand_total = 0

    for item in cart.values():

        order = {
            "order_id": order_id_counter,
            "customer_name": data.customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "subtotal": item["subtotal"],
            "delivery_address": data.delivery_address
        }

        orders.append(order)
        placed_orders.append(order)

        grand_total += item["subtotal"]
        order_id_counter += 1

    cart.clear()

    return {
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }


# ------------------------
# View Orders
# ------------------------

@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }