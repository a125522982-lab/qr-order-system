import json
import os
import time
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MENU_FILE = "menu.json"

# 預設菜單
default_menu = {
    "1": {"name": "招牌牛肉麵", "price": 180},
    "2": {"name": "黃金排骨飯", "price": 150},
    "3": {"name": "手工水餃", "price": 80},
}

# 暫存訂單與已完成訂單
ORDERS = []
COMPLETED_ORDERS = []


def load_menu():
    if not os.path.exists(MENU_FILE):
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(default_menu, f, ensure_ascii=False, indent=4)
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_menu(menu_data):
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(menu_data, f, ensure_ascii=False, indent=4)


@app.route("/")
def index():
    return (
        '<h1>QR Code 點餐系統</h1>'
        '<p><a href="/menu?table=1">前往 1 號桌點餐</a> | '
        '<a href="/admin">前往後台</a></p>'
    )


@app.route("/menu")
def customer_menu():
    table = request.args.get("table", "1")
    return render_template("customer.html", table=table, menu=load_menu())


@app.route("/admin")
def admin_page():
    current_menu = load_menu()
    return render_template(
        "admin.html",
        menu=current_menu,
        orders=ORDERS,
        completed_orders=COMPLETED_ORDERS,
    )


@app.route("/api/menu", methods=["GET", "POST"])
def handle_menu():
    if request.method == "POST":
        data = request.json
        if data:
            save_menu(data)
            return jsonify({"success": True})
        return jsonify({"success": False}), 400
    return jsonify(load_menu())


@app.route("/api/order", methods=["POST"])
def place_order():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "message": "無效資料"}), 400

        # 標準化品項內容，避免亂碼與物件衝突
        raw_items = data.get("items", [])
        cleaned_items = []
        for item in raw_items:
            if isinstance(item, dict):
                cleaned_items.append({
                    "name": str(item.get("name", "未知餐點")),
                    "price": int(item.get("price", 0)),
                    "quantity": int(item.get("quantity", 1)),
                })

        new_order = {
            "id": str(int(time.time() * 1000)),  # 產生唯一的訂單 ID
            "table": str(data.get("table", "1")),
            "items": cleaned_items,
            "total": int(data.get("total", 0)),
        }

        ORDERS.append(new_order)
        return jsonify({"success": True, "message": "ok"})
    except Exception as e:
        print("訂單接收報錯:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/order/complete", methods=["POST"])
def complete_order():
    try:
        data = request.get_json(silent=True)
        if not data or "order_id" not in data:
            return jsonify({"success": False, "message": "無效的訂單編號"}), 400

        target_id = str(data["order_id"])
        
        # 尋找並移動該筆訂單
        found_order = None
        for i, order in enumerate(ORDERS):
            if str(order.get("id")) == target_id:
                found_order = ORDERS.pop(i)
                break

        if found_order:
            COMPLETED_ORDERS.append(found_order)
            return jsonify({"success": True})

        return jsonify({"success": False, "message": "找不到該筆訂單"}), 404
    except Exception as e:
        print("完成訂單報錯:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
