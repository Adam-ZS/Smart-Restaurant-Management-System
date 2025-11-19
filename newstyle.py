from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --------------------------------------------------------
# IN-MEMORY "DATABASE"
# --------------------------------------------------------
MENU = [
    {
        "id": 1,
        "name": "Karak Tea",
        "price": 6,
        "img": "https://foodess.com/wp-content/uploads/2024/02/Karak-Chai-4.jpg",
        "category": "Drinks"
    },
    {
        "id": 2,
        "name": "Pizza",
        "price": 32,
        "img": "https://assets.surlatable.com/m/15a89c2d9c6c1345/72_dpi_webp-REC-283110_Pizza.jpg",
        "category": "Main"
    },
    {
        "id": 3,
        "name": "Chicken Biryani",
        "price": 28,
        "img": "https://www.cubesnjuliennes.com/wp-content/uploads/2020/01/Chicken-Biryani.jpg",
        "category": "Main"
    },
    {
        "id": 4,
        "name": "Rice Plate",
        "price": 15,
        "img": "https://www.allrecipes.com/thmb/TS7Hb4x4owg8zzyTMYhGi739OI0=/750x0/"
               "filters:no_upscale():max_bytes(150000):strip_icc()/microwave-rice-ddmfs-2x3-25-010ae39399ca44d184b57849af4059ad.jpg",
        "category": "Side"
    },
    {
        "id": 5,
        "name": "Mandi",
        "price": 30,
        "img": "https://cdn.prod.website-files.com/5fe870209b4f367ca43b8b48/6913130abb97dd483dbd5f6b_pexels-i-own-my-food-art-76108785-8994586.jpg",
        "category": "Main"
    },
    {
        "id": 6,
        "name": "French Fries",
        "price": 12,
        "img": "https://www.recipetineats.com/tachyon/2022/09/Fries-with-rosemary-salt_1.jpg?resize=900%2C1125&zoom=0.72",
        "category": "Side"
    },
    {
        "id": 7,
        "name": "Chocolate Cake",
        "price": 22,
        "img": "https://sallysbakingaddiction.com/wp-content/uploads/2013/04/triple-chocolate-cake-4.jpg",
        "category": "Dessert"
    }
]

RESERVATIONS = []
ORDERS = []
INVENTORY = [
    {"id": 1, "name": "Rice (kg)", "quantity": 25, "unit": "kg", "low_stock_threshold": 5},
    {"id": 2, "name": "Chicken (kg)", "quantity": 12, "unit": "kg", "low_stock_threshold": 3},
    {"id": 3, "name": "Tea Leaves (kg)", "quantity": 4, "unit": "kg", "low_stock_threshold": 1},
    {"id": 4, "name": "Soft Drinks (bottles)", "quantity": 40, "unit": "bottles", "low_stock_threshold": 10},
]


def now_str():
    return datetime.now().isoformat(timespec="seconds")


def add_log(order, status):
    order.setdefault("log", [])
    order["log"].append({"status": status, "timestamp": now_str()})


# --------------------------------------------------------
# ROOT + HEALTH
# --------------------------------------------------------
@app.get("/")
def root():
    return "SRMS Backend is running. Try /api/health or /api/menu", 200


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "SRMS Backend"})


# --------------------------------------------------------
# AUTH (simple demo)
# --------------------------------------------------------
USERS = {
    "admin": {"password": "admin123", "role": "ADMIN"},
    "waiter": {"password": "waiter123", "role": "WAITER"},
    "chef": {"password": "chef123", "role": "CHEF"},
}

@app.post("/api/login")
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")
    user = USERS.get(username)
    if not user or user["password"] != password:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401
    return jsonify({"success": True, "role": user["role"], "username": username})


# --------------------------------------------------------
# MENU ENDPOINTS
# --------------------------------------------------------
@app.get("/api/menu")
def get_menu():
    return jsonify({"menu": MENU})


@app.put("/api/menu/<int:item_id>")
def update_menu_item(item_id):
    data = request.get_json() or {}
    item = next((m for m in MENU if m["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Menu item not found"}), 404

    if "name" in data:
        item["name"] = data["name"]
    if "price" in data:
        item["price"] = float(data["price"])
    if "category" in data:
        item["category"] = data["category"]

    return jsonify(item)


# --------------------------------------------------------
# INVENTORY ENDPOINTS
# --------------------------------------------------------
@app.get("/api/inventory")
def get_inventory():
    return jsonify({"inventory": INVENTORY})


@app.put("/api/inventory/<int:item_id>")
def update_inventory_item(item_id):
    data = request.get_json() or {}
    inv = next((x for x in INVENTORY if x["id"] == item_id), None)
    if not inv:
        return jsonify({"error": "Inventory item not found"}), 404

    if "quantity" in data:
        inv["quantity"] = float(data["quantity"])
    if "low_stock_threshold" in data:
        inv["low_stock_threshold"] = float(data["low_stock_threshold"])

    return jsonify(inv)


# --------------------------------------------------------
# RESERVATIONS ENDPOINTS
# --------------------------------------------------------
@app.post("/api/reservations")
def create_reservation():
    data = request.get_json() or {}

    new_res = {
        "id": len(RESERVATIONS) + 1,
        "name": data.get("name", "Guest"),
        "date": data.get("date", ""),
        "time": data.get("time", ""),
        "size": data.get("size", 1),
        "created_at": now_str()
    }

    RESERVATIONS.append(new_res)
    return jsonify(new_res), 201


@app.get("/api/reservations")
def list_reservations():
    return jsonify({"reservations": RESERVATIONS})


# --------------------------------------------------------
# ORDERS ENDPOINTS
# --------------------------------------------------------
VALID_STATUSES = [
    "RECEIVED", "PREPARING", "READY",
    "OUT_FOR_DELIVERY", "COMPLETED", "CANCELLED"
]

@app.post("/api/orders")
def create_order():
    data = request.get_json() or {}

    items = data.get("items", [])
    order_type = data.get("order_type", "WALK_IN")  # WALK_IN / DINE_IN / DELIVERY
    table_no = data.get("table_no")
    delivery_address = data.get("delivery_address")
    customer_name = data.get("customer_name", "Guest")

    total = 0
    normalized_items = []

    # Normalize items (id-based or full objects)
    for item in items:
        if isinstance(item, dict) and "price" in item and "name" in item:
            qty = int(item.get("qty", 1))
            normalized_items.append({
                "id": item.get("id"),
                "name": item["name"],
                "price": float(item["price"]),
                "qty": qty
            })
            total += float(item["price"]) * qty
        elif isinstance(item, int):
            m = next((x for x in MENU if x["id"] == item), None)
            if m:
                normalized_items.append({
                    "id": m["id"],
                    "name": m["name"],
                    "price": float(m["price"]),
                    "qty": 1
                })
                total += float(m["price"])

    new_order = {
        "id": len(ORDERS) + 1,
        "customer_name": customer_name,
        "order_type": order_type,   # WALK_IN / DINE_IN / DELIVERY
        "table_no": table_no,
        "delivery_address": delivery_address,
        "items": normalized_items,
        "total": total,
        "status": "RECEIVED",
        "created_at": now_str(),
        "updated_at": now_str()
    }
    add_log(new_order, "RECEIVED")

    ORDERS.append(new_order)
    return jsonify(new_order), 201


@app.get("/api/orders")
def list_orders():
    """
    Optional filters:
        ?status=PREPARING
        ?order_type=DINE_IN
        ?for=kitchen  (only RECEIVED/PREPARING)
    """
    status = request.args.get("status")
    order_type = request.args.get("order_type")
    for_kitchen = request.args.get("for") == "kitchen"

    result = ORDERS
    if status:
        result = [o for o in result if o["status"] == status]
    if order_type:
        result = [o for o in result if o["order_type"] == order_type]
    if for_kitchen:
        result = [o for o in result if o["status"] in ("RECEIVED", "PREPARING")]

    return jsonify({"orders": result})


@app.get("/api/orders/<int:order_id>")
def get_order(order_id):
    o = next((x for x in ORDERS if x["id"] == order_id), None)
    if not o:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(o)


@app.patch("/api/orders/<int:order_id>/status")
def update_order_status(order_id):
    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status not in VALID_STATUSES:
        return jsonify({"error": "Invalid status"}), 400

    o = next((x for x in ORDERS if x["id"] == order_id), None)
    if not o:
        return jsonify({"error": "Order not found"}), 404

    o["status"] = new_status
    o["updated_at"] = now_str()
    add_log(o, new_status)
    return jsonify(o)


# --------------------------------------------------------
# ANALYTICS ENDPOINT
# --------------------------------------------------------
@app.get("/api/analytics")
def analytics():
    total_orders = len(ORDERS)
    total_revenue = sum(o.get("total", 0) for o in ORDERS)

    # Count items
    counts = {}
    for o in ORDERS:
        for it in o.get("items", []):
            n = it.get("name", "Unknown")
            counts[n] = counts.get(n, 0) + int(it.get("qty", 1))

    # Sort top items
    top_items = sorted(
        [{"name": k, "count": v} for k, v in counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )

    return jsonify({
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "top_items": top_items
    })


# --------------------------------------------------------
# START SERVER
# --------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
