from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field, PositiveInt

app = FastAPI(title="FastAPI Food Delivery App")

# ------------------
# In-memory "database"
# ------------------
menu_items: List[Dict[str, Any]] = []
orders: List[Dict[str, Any]] = []
cart: Dict[str, Any] = {"items": []}

_next_menu_id = 1
_next_order_id = 1


# ------------------
# Pydantic Models
# ------------------
class MenuCategory(str, Enum):
    pizza = "pizza"
    burger = "burger"
    snack = "snack"
    drinks = "drinks"


class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    price: float = Field(..., gt=0, le=1000)
    category: MenuCategory


class MenuItemCreate(MenuItemBase):
    available: bool = True


class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    price: Optional[float] = Field(None, gt=0, le=1000)
    category: Optional[MenuCategory]
    available: Optional[bool]


class MenuItem(MenuItemBase):
    id: int
    available: bool


class CartItem(BaseModel):
    item_id: int
    quantity: PositiveInt = 1


class OrderStatus(str, Enum):
    pending = "pending"
    preparing = "preparing"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"


class Order(BaseModel):
    id: int
    items: List[CartItem]
    total: float
    status: OrderStatus
    created_at: datetime


# ------------------
# Helper functions
# ------------------

def _get_next_menu_id() -> int:
    global _next_menu_id
    value = _next_menu_id
    _next_menu_id += 1
    return value


def _get_next_order_id() -> int:
    global _next_order_id
    value = _next_order_id
    _next_order_id += 1
    return value


def find_menu_item(item_id: int) -> Optional[Dict[str, Any]]:
    for item in menu_items:
        if item["id"] == item_id:
            return item
    return None


def calculate_order_total(items: List[Dict[str, Any]]) -> float:
    return round(sum(i["price"] * i["quantity"] for i in items), 2) if items else 0.0


def filter_menu_items(
    keyword: Optional[str] = None,
    category: Optional[MenuCategory] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    available: Optional[bool] = None,
) -> List[Dict[str, Any]]:
    results = menu_items

    if keyword is not None:
        keyword_lower = keyword.strip().lower()
        results = [
            item
            for item in results
            if keyword_lower in item["name"].lower()
            or (item.get("description") and keyword_lower in item["description"].lower())
        ]

    if category is not None:
        results = [item for item in results if item["category"] == category.value]

    if min_price is not None:
        results = [item for item in results if item["price"] >= min_price]

    if max_price is not None:
        results = [item for item in results if item["price"] <= max_price]

    if available is not None:
        results = [item for item in results if item["available"] == available]

    return results


def _apply_sorting(
    data: List[Dict[str, Any]], sort_by: str, order: str
) -> List[Dict[str, Any]]:
    reverse = order == "desc"
    if sort_by not in {"name", "price", "category"}:
        raise HTTPException(status_code=400, detail="sort_by must be one of: name, price, category")
    return sorted(data, key=lambda x: x[sort_by], reverse=reverse)


def _paginate(data: List[Dict[str, Any]], page: int, limit: int) -> Dict[str, Any]:
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="page and limit must be positive integers")

    total = len(data)
    start = (page - 1) * limit
    end = start + limit
    page_data = data[start:end]
    total_pages = (total + limit - 1) // limit

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "items": page_data,
    }


# ------------------
# Day 1: GET endpoints
# ------------------

@app.get("/", summary="Home route")
def home() -> Dict[str, str]:
    return {"message": "Welcome to the FastAPI Food Delivery App"}


@app.get("/menu", response_model=List[MenuItem], summary="List all menu items")
def get_menu() -> List[MenuItem]:
    return [MenuItem(**item) for item in menu_items]


@app.get("/menu/summary", summary="Menu summary")
def menu_summary() -> Dict[str, Any]:
    return {"total_items": len(menu_items), "available_items": sum(1 for i in menu_items if i["available"]) }


# ------------------
# Day 2: POST + Pydantic
# ------------------

@app.post(
    "/menu",
    response_model=MenuItem,
    status_code=status.HTTP_201_CREATED,
    summary="Create a menu item",
)
def create_menu_item(item: MenuItemCreate) -> MenuItem:
    # Duplicate check
    for existing in menu_items:
        if existing["name"].strip().lower() == item.name.strip().lower():
            raise HTTPException(status_code=400, detail="Menu item with the same name already exists")

    new_item = item.dict()
    # store enum values as strings to simplify filtering/sorting
    new_item["category"] = new_item["category"].value
    new_item["id"] = _get_next_menu_id()
    menu_items.append(new_item)
    return MenuItem(**new_item)


# ------------------
# Day 3: Helpers + Filter
# ------------------

@app.get(
    "/menu/search",
    response_model=List[MenuItem],
    summary="Search menu items",
)
def search_menu(
    keyword: Optional[str] = Query(None, description="Search keyword"),
    category: Optional[MenuCategory] = Query(None, description="Category filter"),
    min_price: Optional[float] = Query(None, gt=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, gt=0, description="Maximum price"),
    available: Optional[bool] = Query(None, description="Availability filter"),
) -> List[MenuItem]:
    results = filter_menu_items(keyword, category, min_price, max_price, available)

    if not results:
        raise HTTPException(status_code=404, detail="No menu items match the search criteria")

    return [MenuItem(**item) for item in results]


# ------------------
# Day 4: CRUD (PUT, DELETE)
# ------------------

# ------------------

@app.get("/cart", summary="Get current cart")
def get_cart() -> Dict[str, Any]:
    return cart


@app.post("/cart/add", status_code=status.HTTP_201_CREATED, summary="Add item to cart")
def add_to_cart(cart_item: CartItem) -> Dict[str, Any]:
    item = find_menu_item(cart_item.item_id)
    if not item or not item["available"]:
        raise HTTPException(status_code=404, detail="Item not available")

    for existing in cart["items"]:
        if existing["item_id"] == cart_item.item_id:
            existing["quantity"] += cart_item.quantity
            return cart

    cart["items"].append(cart_item.dict())
    return cart


@app.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED, summary="Place an order")
def place_order() -> Order:
    if not cart["items"]:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order_items = []
    for ci in cart["items"]:
        item = find_menu_item(ci["item_id"])
        if not item or not item["available"]:
            raise HTTPException(
                status_code=400,
                detail=f"Item {ci['item_id']} is not available, please update your cart",
            )
        order_items.append({"item_id": ci["item_id"], "quantity": ci["quantity"], "price": item["price"]})

    total = round(sum(i["quantity"] * i["price"] for i in order_items), 2)
    new_order = {
        "id": _get_next_order_id(),
        "items": order_items,
        "total": total,
        "status": OrderStatus.pending.value,
        "created_at": datetime.utcnow(),
    }
    orders.append(new_order)

    cart["items"] = []
    return Order(**new_order)


@app.get("/orders", response_model=List[Order], summary="List all orders")
def list_orders() -> List[Order]:
    return [Order(**o) for o in orders]


@app.get("/orders/{order_id}", response_model=Order, summary="Get order by ID")
def get_order(order_id: int) -> Order:
    for order in orders:
        if order["id"] == order_id:
            return Order(**order)
    raise HTTPException(status_code=404, detail="Order not found")


@app.post(
    "/orders/{order_id}/status",
    response_model=Order,
    summary="Update order status",
)
def update_order_status(order_id: int, status: OrderStatus) -> Order:
    order = next((o for o in orders if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order["status"] = status.value
    return Order(**order)


# ------------------
# Day 6: Advanced APIs (Search, Sort, Pagination)
# ------------------

@app.get(
    "/menu/sort",
    response_model=List[MenuItem],
    summary="Sort menu items",
)
def sort_menu(
    sort_by: str = Query("name", regex="^(name|price|category)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
) -> List[MenuItem]:
    sorted_items = _apply_sorting(menu_items, sort_by, order)
    return [MenuItem(**item) for item in sorted_items]


@app.get(
    "/menu/paginate",
    summary="Paginate menu items",
)
def paginate_menu(
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=50),
) -> Dict[str, Any]:
    return _paginate(menu_items, page, limit)


@app.get(
    "/orders/browse",
    summary="Browse orders with search, sort, and pagination",
)
def browse_orders(
    keyword: Optional[str] = Query(None, description="Search in order IDs or item names"),
    sort_by: str = Query("id", regex="^(id|total|created_at)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=50),
) -> Dict[str, Any]:
    data = orders

    if keyword:
        keyword_lower = keyword.strip().lower()

        def order_contains_keyword(order: Dict[str, Any]) -> bool:
            if keyword_lower in str(order["id"]).lower():
                return True
            for oi in order["items"]:
                menu_item = find_menu_item(oi["item_id"])
                if menu_item and keyword_lower in menu_item["name"].lower():
                    return True
            return False

        data = [o for o in data if order_contains_keyword(o)]

    reverse = order == "desc"
    if sort_by == "created_at":
        data = sorted(data, key=lambda x: x["created_at"], reverse=reverse)
    else:
        data = sorted(data, key=lambda x: x[sort_by], reverse=reverse)

    return _paginate(data, page, limit)


@app.get(
    "/browse",
    summary="Combined browsing endpoint (search + sort + pagination)",
)
def browse_menu(
    keyword: Optional[str] = Query(None, description="Keyword search"),
    category: Optional[MenuCategory] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, gt=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, gt=0, description="Maximum price"),
    sort_by: str = Query("name", regex="^(name|price|category)$"),
    order: str = Query("asc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=50),
) -> Dict[str, Any]:
    results = filter_menu_items(keyword, category, min_price, max_price)
    results = _apply_sorting(results, sort_by, order)
    return _paginate(results, page, limit)


@app.get("/menu/{item_id}", response_model=MenuItem, summary="Get menu item by ID")
def get_menu_item(item_id: int) -> MenuItem:
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return MenuItem(**item)


@app.put(
    "/menu/{item_id}",
    response_model=MenuItem,
    summary="Update menu item",
)
def update_menu_item(item_id: int, item_update: MenuItemUpdate) -> MenuItem:
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    update_data = item_update.dict(exclude_unset=True)
    if "category" in update_data and isinstance(update_data["category"], Enum):
        update_data["category"] = update_data["category"].value

    for key, value in update_data.items():
        item[key] = value

    return MenuItem(**item)


@app.delete(
    "/menu/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete menu item",
)
def delete_menu_item(item_id: int) -> None:
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    # Business rule: cannot delete if item is in a pending order
    for order in orders:
        if order["status"] != OrderStatus.delivered.value:
            for oi in order["items"]:
                if oi["item_id"] == item_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot delete menu item while it exists in an active order",
                    )

    menu_items.remove(item)


@app.on_event("startup")
def _load_sample_data() -> None:
    # Seed with a few menu items for testing in Swagger UI
    if not menu_items:
        sample_items = [
            {"name": "Margherita Pizza", "description": "Classic cheese and tomato", "price": 9.99, "category": "pizza", "available": True},
            {"name": "Veggie Burger", "description": "Plant-based patty with salad", "price": 8.49, "category": "burger", "available": True},
            {"name": "French Fries", "description": "Crispy potato fries", "price": 3.99, "category": "snack", "available": True},
            {"name": "Cold Soda", "description": "Refreshing fizzy drink", "price": 1.99, "category": "drinks", "available": True},
        ]
        for item in sample_items:
            item["id"] = _get_next_menu_id()
            menu_items.append(item)
