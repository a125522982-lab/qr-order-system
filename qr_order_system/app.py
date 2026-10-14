from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# 將 MENU 改為全域變數，支援動態新增與刪除
MENU = [
    {"id": 1, "name": "招牌牛肉麵", "price": 180, "category": "主食"},
    {"id": 2, "name": "日系豚骨拉麵", "price": 200, "category": "主食"},
    {"id": 3, "name": "黃金脆皮炸雞", "price": 120, "category": "點心"},
    {"id": 4, "name": "經典可口可樂", "price": 40, "category": "飲料"},
]

orders = []
order_id_counter = 1
menu_id_counter = 5  # 用於新菜單的 ID 遞增


@app.route("/")
def index():
    return "QR Code 點餐系統伺服器運行中！請前往 /menu?table=1 或 /admin 查看。"


# 顧客點餐頁面
@app.route("/menu")
def customer_menu():
    table = request.args.get("table", "1")
    return render_template("customer.html", table=table, menu=MENU)


# 取得目前菜單的 API (供後台或前端即時讀取)
@app.route("/api/menu", methods=["GET"])
def get_menu():
    return jsonify(MENU)


# 新增菜單品項
@app.route("/api/menu", methods=["POST"])
def add_menu_item():
    global menu_id_counter
    data = request.json
    name = data.get("name")
    price = data.get("price")
    category = data.get("category", "主食")

    if not name or not price:
        return jsonify({"status": "error", "message": "請填寫品項名稱與價格"}), 400

    new_item = {
        "id": menu_id_counter,
        "name": name,
        "price": int(price),
        "category": category,
    }
    MENU.append(new_item)
    menu_id_counter += 1

    return jsonify({"status": "success", "item": new_item})


# 刪除菜單品項
@app.route("/api/menu/<int:item_id>", methods=["DELETE"])
def delete_menu_item(item_id):
    global MENU
    MENU = [item for item in MENU if item["id"] != item_id]
    return jsonify({"status": "success", "message": "已刪除品項"})


# 接收顧客送出的訂單
@app.route("/api/orders", methods=["POST"])
def create_order():
    global order_id_counter
    data = request.json
    table = data.get("table")
    items = data.get("items")

    if not items:
        return jsonify({"status": "error", "message": "購物車是空的"}), 400

    total_price = 0
    detailed_items = []
    for item in items:
        menu_item = next(
            (m for m in MENU if m["id"] == int(item["id"])), None
        )
        if menu_item:
            subtotal = menu_item["price"] * item["quantity"]
            total_price += subtotal
            detailed_items.append(
                {
                    "name": menu_item["name"],
                    "price": menu_item["price"],
                    "quantity": item["quantity"],
                    "subtotal": subtotal,
                }
            )

    new_order = {
        "order_id": order_id_counter,
        "table": table,
        "items": detailed_items,
        "total_price": total_price,
        "status": "未出餐",
    }

    orders.append(new_order)
    order_id_counter += 1

    return jsonify({"status": "success", "order": new_order})


# 店家後台頁面
@app.route("/admin")
def admin_page():
    return render_template("admin.html")


# 取得所有訂單的 API
@app.route("/api/orders", methods=["GET"])
def get_orders():
    return jsonify(orders)


# 更新訂單狀態
@app.route("/api/orders/<int:order_id>/status", methods=["PUT"])
def update_order_status(order_id):
    data = request.json
    new_status = data.get("status")
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = new_status
            return jsonify({"status": "success", "order": order})
    return jsonify({"status": "error", "message": "找不到訂單"}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)