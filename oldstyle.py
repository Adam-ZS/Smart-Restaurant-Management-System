from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# --------------------------------------------------------
# SIMPLE IN-MEMORY "DATABASE"
# --------------------------------------------------------

USERS = [
    {"username": "admin",  "password": "admin123",  "role": "ADMIN"},
    {"username": "waiter", "password": "waiter123", "role": "WAITER"},
    {"username": "chef",   "password": "chef123",   "role": "CHEF"},
]

MENU = [
    {
        "id": 1,
        "name": "Karak Tea",
        "price": 6.0,
        "category": "Drinks",
        "img": "https://foodess.com/wp-content/uploads/2024/02/Karak-Chai-4.jpg"
    },
    {
        "id": 2,
        "name": "Pizza",
        "price": 32.0,
        "category": "Main",
        "img": "https://assets.surlatable.com/m/15a89c2d9c6c1345/72_dpi_webp-REC-283110_Pizza.jpg"
    },
    {
        "id": 3,
        "name": "Chicken Biryani",
        "price": 28.0,
        "category": "Main",
        "img": "https://www.cubesnjuliennes.com/wp-content/uploads/2020/01/Chicken-Biryani.jpg"
    },
    {
        "id": 4,
        "name": "Rice Plate",
        "price": 15.0,
        "category": "Side",
        "img": "https://www.allrecipes.com/thmb/TS7Hb4x4owg8zzyTMYhGi739OI0=/750x0/"
               "filters:no_upscale():max_bytes(150000):strip_icc()/microwave-rice-ddmfs-2x3-25-010ae39399ca44d184b57849af4059ad.jpg"
    },
    {
        "id": 5,
        "name": "Mandi",
        "price": 30.0,
        "category": "Main",
        "img": "https://cdn.prod.website-files.com/5fe870209b4f367ca43b8b48/6913130abb97dd483dbd5f6b_pexels-i-own-my-food-art-76108785-8994586.jpg"
    },
    {
        "id": 6,
        "name": "French Fries",
        "price": 12.0,
        "category": "Side",
        "img": "https://www.recipetineats.com/tachyon/2022/09/Fries-with-rosemary-salt_1.jpg?resize=900%2C1125&zoom=0.72"
    },
    {
        "id": 7,
        "name": "Chocolate Cake",
        "price": 22.0,
        "category": "Dessert",
        "img": "https://sallysbakingaddiction.com/wp-content/uploads/2013/04/triple-chocolate-cake-4.jpg"
    },
]

# Simple inventory for some ingredients / items
INVENTORY = [
    {"id": 1, "name": "Rice (kg)", "qty": 25, "unit": "kg", "low_stock_threshold": 5},
    {"id": 2, "name": "Chicken (kg)", "qty": 15, "unit": "kg", "low_stock_threshold": 4},
    {"id": 3, "name": "Tea Leaves (kg)", "qty": 3, "unit": "kg", "low_stock_threshold": 2},
    {"id": 4, "name": "Soft Drinks (bottles)", "qty": 40, "unit": "pcs", "low_stock_threshold": 10},
    {"id": 5, "name": "French Fries (kg)", "qty": 10, "unit": "kg", "low_stock_threshold": 3},
]

RESERVATIONS = []  # { id, name, date, time, size }
ORDERS = []        # see structure below

# --------------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------------

def now_iso():
    return datetime.utcnow().isoformat() + "Z"


def find_menu_item(menu_id):
    return next((m for m in MENU if m["id"] == menu_id), None)


def add_log(order, message):
    order.setdefault("logs", [])
    order["logs"].append({
        "timestamp": now_iso(),
        "message": message,
        "status": order.get("status")
    })


def recalc_inventory_for_order(order):
    """
    Very simplified demo:
    - For each item, subtract 1 unit from some inventory lines
      (You can make mapping item->ingredient if you want.)
    """
    for inv in INVENTORY:
        if inv["name"].startswith("Rice") and any("Mandi" in it["name"] or "Biryani" in it["name"] for it in order["items"]):
            inv["qty"] = max(inv["qty"] - 1, 0)
        if inv["name"].startswith("Tea") and any("Karak" in it["name"] for it in order["items"]):
            inv["qty"] = max(inv["qty"] - 0.1, 0)


def low_stock_items():
    alerts = []
    for inv in INVENTORY:
        if inv["qty"] <= inv["low_stock_threshold"]:
            alerts.append(inv)
    return alerts


def simple_recommendations(current_item_ids):
    """
    Simple "AI-style" collaborative filter:
    - If certain item in cart, recommend others that match category
    - fallback: top 3 most expensive items not in cart
    """
    if not current_item_ids:
        return []

    current_items = [m for m in MENU if m["id"] in current_item_ids]
    current_cats = {m["category"] for m in current_items}

    candidates = [m for m in MENU if m["id"] not in current_item_ids and m["category"] in current_cats]
    if not candidates:
        candidates = [m for m in MENU if m["id"] not in current_item_ids]

    candidates_sorted = sorted(candidates, key=lambda x: x["price"], reverse=True)
    return candidates_sorted[:3]


# --------------------------------------------------------
# ROOT + HEALTH
# --------------------------------------------------------

@app.get("/")
def root():
    return "SRMS Backend is running. Try /api/health or /api/menu", 200


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "SRMS Backend", "time": now_iso()})


# --------------------------------------------------------
# AUTH / LOGIN
# --------------------------------------------------------

@app.post("/api/auth/login")
def login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")

    user = next((u for u in USERS if u["username"] == username and u["password"] == password), None)
    if not user:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    # Very simple demo: we don't generate JWT, only return role/username
    return jsonify({
        "success": True,
        "username": user["username"],
        "role": user["role"]
    })


# --------------------------------------------------------
# MENU ENDPOINTS (Customer + Admin)
# --------------------------------------------------------

@app.get("/api/menu")
def get_menu():
    return jsonify({"menu": MENU})


@app.patch("/api/menu/<int:menu_id>")
def update_menu_item(menu_id):
    """Admin updates item price or name."""
    data = request.get_json() or {}
    item = find_menu_item(menu_id)
    if not item:
        return jsonify({"error": "Menu item not found"}), 404

    if "name" in data:
        item["name"] = data["name"]
    if "price" in data:
        try:
            item["price"] = float(data["price"])
        except ValueError:
            return jsonify({"error": "Invalid price"}), 400
    if "category" in data:
        item["category"] = data["category"]

    return jsonify(item)


# --------------------------------------------------------
# INVENTORY (Admin)
# --------------------------------------------------------

@app.get("/api/inventory")
def get_inventory():
    return jsonify({
        "inventory": INVENTORY,
        "low_stock": low_stock_items()
    })


@app.patch("/api/inventory/<int:item_id>")
def update_inventory(item_id):
    data = request.get_json() or {}
    item = next((i for i in INVENTORY if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Inventory item not found"}), 404

    if "qty" in data:
        try:
            item["qty"] = float(data["qty"])
        except ValueError:
            return jsonify({"error": "Invalid qty"}), 400
    if "low_stock_threshold" in data:
        try:
            item["low_stock_threshold"] = float(data["low_stock_threshold"])
        except ValueError:
            return jsonify({"error": "Invalid threshold"}), 400

    return jsonify(item)


# --------------------------------------------------------
# RESERVATIONS (Customer + Admin)
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
        "created_at": now_iso()
    }

    RESERVATIONS.append(new_res)
    return jsonify(new_res), 201


@app.get("/api/reservations")
def list_reservations():
    return jsonify({"reservations": RESERVATIONS})


# --------------------------------------------------------
# ORDERS
# --------------------------------------------------------
"""
Order structure example:

{
  "id": 1,
  "customer_name": "Walk-in Customer",
  "type": "WALK_IN" | "DINE_IN" | "DELIVERY",
  "table_number": "T1" (if dine in),
  "delivery_address": "..." (if delivery),
  "items": [
      { "menu_id": 2, "name": "Pizza", "price": 32.0, "qty": 1 }
  ],
  "status": "RECEIVED" | "PREPARING" | "READY" | "OUT_FOR_DELIVERY" | "COMPLETED" | "CANCELLED",
  "created_at": "...",
  "updated_at": "...",
  "logs": [ { timestamp, status, message } ]
}
"""


@app.post("/api/orders")
def create_order():
    data = request.get_json() or {}

    customer_name = data.get("customer_name", "Guest")
    order_type = data.get("type", "WALK_IN")  # WALK_IN, DINE_IN, DELIVERY
    table_number = data.get("table_number")
    delivery_address = data.get("delivery_address")
    raw_items = data.get("items", [])  # could be ids or full objects

    items = []
    total = 0.0

    for it in raw_items:
        if isinstance(it, dict):
            # if front-end sends full item
            menu_id = it.get("id") or it.get("menu_id")
            qty = it.get("qty", 1)
            menu_item = find_menu_item(menu_id) if menu_id else None
            if menu_item:
                price = float(menu_item["price"])
                items.append({
                    "menu_id": menu_item["id"],
                    "name": menu_item["name"],
                    "price": price,
                    "qty": qty
                })
                total += price * qty
        elif isinstance(it, int):
            # if front-end sends only id
            menu_item = find_menu_item(it)
            if menu_item:
                price = float(menu_item["price"])
                items.append({
                    "menu_id": menu_item["id"],
                    "name": menu_item["name"],
                    "price": price,
                    "qty": 1
                })
                total += price

    order = {
        "id": len(ORDERS) + 1,
        "customer_name": customer_name,
        "type": order_type,
        "table_number": table_number,
        "delivery_address": delivery_address,
        "items": items,
        "total": total,
        "status": "RECEIVED",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "logs": []
    }
    add_log(order, "Order created")

    # adjust inventory
    recalc_inventory_for_order(order)

    ORDERS.append(order)
    return jsonify(order), 201


@app.get("/api/orders")
def list_orders():
    """
    Optional query filter:
    - status: RECEIVED, PREPARING, READY, OUT_FOR_DELIVERY, COMPLETED
    - type: WALK_IN, DINE_IN, DELIVERY
    """
    status = request.args.get("status")
    otype = request.args.get("type")

    result = ORDERS
    if status:
        result = [o for o in result if o["status"] == status]
    if otype:
        result = [o for o in result if o["type"] == otype]

    return jsonify({"orders": result})


@app.get("/api/orders/<int:order_id>")
def get_order(order_id):
    order = next((o for o in ORDERS if o["id"] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order)


@app.patch("/api/orders/<int:order_id>/status")
def update_order_status(order_id):
    data = request.get_json() or {}
    new_status = data.get("status")

    valid_statuses = [
        "RECEIVED", "PREPARING", "READY",
        "OUT_FOR_DELIVERY", "COMPLETED", "CANCELLED"
    ]

    if new_status not in valid_statuses:
        return jsonify({"error": "Invalid status"}), 400

    order = next((o for o in ORDERS if o["id"] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    order["status"] = new_status
    order["updated_at"] = now_iso()
    add_log(order, f"Status changed to {new_status}")
    return jsonify(order)


# --------------------------------------------------------
# KITCHEN QUEUE (KDS)
# --------------------------------------------------------

@app.get("/api/kitchen/queue")
def kitchen_queue():
    """
    For Chef tablet:
    - show all orders NOT completed/cancelled
    - sorted by created_at
    """
    active = [o for o in ORDERS if o["status"] not in ("COMPLETED", "CANCELLED")]
    active_sorted = sorted(active, key=lambda o: o["created_at"])
    return jsonify({"orders": active_sorted})


# --------------------------------------------------------
# AI RECOMMENDATIONS
# --------------------------------------------------------

@app.post("/api/recommendations")
def recommendations():
    """
    Input: { "item_ids": [2,3] }
    Output: { "recommendations": [ ...menu items... ] }
    """
    data = request.get_json() or {}
    ids = data.get("item_ids", [])
    recs = simple_recommendations(ids)
    return jsonify({"recommendations": recs})


# --------------------------------------------------------
# ANALYTICS
# --------------------------------------------------------

@app.get("/api/analytics")
def analytics():
    total_orders = len(ORDERS)
    total_revenue = sum(o.get("total", 0) for o in ORDERS)

    # Count items sold
    counts = {}
    for o in ORDERS:
        for it in o.get("items", []):
            name = it.get("name", "Unknown")
            counts[name] = counts.get(name, 0) + it.get("qty", 1)

    top_items = sorted(
        [{"name": k, "count": v} for k, v in counts.items()],
        key=lambda x: x["count"],
        reverse=True
    )

    return jsonify({
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "top_items": top_items,
        "low_stock": low_stock_items()
    })


# --------------------------------------------------------
# MAIN
# --------------------------------------------------------

if __name__ == "__main__":
    # For local dev
    app.run(debug=True)
