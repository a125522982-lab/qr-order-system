import json
import os
import time
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MENU_FILE = "menu.json"

default_menu = {
    "101": {"name": "無骨雞腿排", "price": 90, "is_sold_out": False},
    "102": {"name": "脆皮香雞排", "price": 75, "is_sold_out": False},
    "103": {"name": "雞腿", "price": 55, "is_sold_out": False},
    "104": {"name": "雞塊", "price": 55, "is_sold_out": False},
    "105": {"name": "雞翅", "price": 35, "is_sold_out": False},
    "106": {"name": "乳酪棒 (4)", "price": 50, "is_sold_out": False},
    "107": {"name": "芋泥球 (8)", "price": 50, "is_sold_out": False},
    "108": {"name": "起司球 (4)", "price": 50, "is_sold_out": False},
    "109": {"name": "甜不辣", "price": 35, "is_sold_out": False},
    "110": {"name": "百頁豆腐", "price": 30, "is_sold_out": False},
    "111": {"name": "米血 (6)", "price": 30, "is_sold_out": False},
    "112": {"name": "帶皮薯瓣", "price": 60, "is_sold_out": False},
    "113": {"name": "杏鮑菇", "price": 55, "is_sold_out": False},
    "114": {"name": "深海鱈魚條 (2)", "price": 40, "is_sold_out": False},
    "115": {"name": "娘惹山藥捲 (4)", "price": 40, "is_sold_out": False},
    "116": {"name": "雞軟骨", "price": 60, "is_sold_out": False},
    "117": {"name": "魷米花", "price": 60, "is_sold_out": False},
    "118": {"name": "嗑嗑雞丁", "price": 65, "is_sold_out": False},
    "119": {"name": "雞皮", "price": 40, "is_sold_out": False},
    "120": {"name": "美式脆薯", "price": 45, "is_sold_out": False},
    "121": {"name": "薯餅 (4)", "price": 40, "is_sold_out": False},
    "122": {"name": "花枝丸 (5)", "price": 40, "is_sold_out": False},
    "123": {"name": "麥嗑雞塊 (5)", "price": 45, "is_sold_out": False},
    "124": {"name": "洋蔥圈 (6)", "price": 40, "is_sold_out": False},
    "125": {"name": "煉香花月圓", "price": 40, "is_sold_out": False},
    "126": {"name": "煉乳銀絲卷 (4)", "price": 40, "is_sold_out": False},
    "127": {"name": "椒鹽銀絲卷 (4)", "price": 30, "is_sold_out": False},
    "128": {"name": "黃金地瓜條", "price": 50, "is_sold_out": False},
    "129": {"name": "起司薯球 (6)", "price": 50, "is_sold_out": False},
    "201": {"name": "1號餐 (雞翅+雞塊+飲料)", "price": 100, "is_sold_out": False},
    "202": {"name": "2號餐 (雞塊+雞腿+飲料)", "price": 120, "is_sold_out": False},
    "203": {"name": "3號餐 (美式脆薯+嗑嗑雞丁+麥嗑雞塊+飲料)", "price": 140, "is_sold_out": False},
    "204": {"name": "4號餐 (雞腿+雞塊+雞翅+飲料)", "price": 155, "is_sold_out": False},
    "205": {"name": "5號餐 (雞排+美式脆薯+飲料)", "price": 125, "is_sold_out": False},
    "206": {"name": "全家桶", "price": 339, "is_sold_out": False},
    "207": {"name": "超值全家桶", "price": 449, "is_sold_out": False},
    "208": {"name": "炸全雞", "price": 429, "is_sold_out": False},
    "209": {"name": "全雞餐", "price": 579, "is_sold_out": False},
    "210": {"name": "雞翅滿足桶", "price": 399, "is_sold_out": False},
    "211": {"name": "雞塊滿足桶", "price": 399, "is_sold_out": False},
    "212": {"name": "雞腿滿足桶", "price": 399, "is_sold_out": False},
}

ORDERS = []
ACCEPTED_ORDERS = []
COMPLETED_ORDERS = []


def load_menu():
    if not os.path.exists(MENU_FILE):
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(default_menu, f, ensure_ascii=False, indent=4)
    try:
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data and isinstance(data, dict):
                for item_id, item_info in data.items():
                    if "is_sold_out" not in item_info:
                        item_info["is_sold_out"] = False
                return data
    except Exception:
        pass
    return default_menu


def save_menu(menu_data):
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(menu_data, f, ensure_ascii=False, indent=4)


@app.route("/")
def index():
    return (
        '<h1>酷嗑斯美式炸雞 - 點餐系統</h1>'
        '<p><a href="/menu?table=1">前往 1 號桌點餐</a> | '
        '<a href="/admin">前往後台</a></p>'
    )


@app.route("/menu")
def customer_menu():
    table = request.args.get("table", "1")
    return render_template("customer.html", table=table, menu=load_menu())


@app.route("/admin")
def admin_page():
    global ORDERS, ACCEPTED_ORDERS, COMPLETED_ORDERS
    current_menu = load_menu()
    
    def clean_list(lst):
        cleaned = []
        for o in lst:
            if isinstance(o, dict) and callable(o.get("food_list")) is False:
                fl = o.get("food_list", [])
                if isinstance(fl, list):
                    phone = str(o.get("phone", "0000000000"))
                    # 自動擷取完整電話的後四碼作為取餐編號
                    phone_last4 = phone[-4:] if len(phone) >= 4 else "0000"
                    cleaned.append({
                        "id": str(o.get("id", time.time())),
                        "table": str(o.get("table", "1")),
                        "phone": phone,
                        "phone_last4": phone_last4,
                        "food_list": fl,
                        "total": int(o.get("total", 0))
                    })
        return cleaned

    ORDERS = clean_list(ORDERS)
    ACCEPTED_ORDERS = clean_list(ACCEPTED_ORDERS)
    COMPLETED_ORDERS = clean_list(COMPLETED_ORDERS)

    return render_template(
        "admin.html",
        menu=current_menu,
        orders=ORDERS,
        accepted_orders=ACCEPTED_ORDERS,
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


@app.route("/api/menu/toggle_soldout", methods=["POST"])
def toggle_soldout():
    try:
        data = request.get_json(silent=True)
        if not data or "item_id" not in data:
            return jsonify({"success": False, "message": "無效的品項代號"}), 400

        item_id = str(data["item_id"])
        menu = load_menu()

        if item_id in menu:
            current_status = menu[item_id].get("is_sold_out", False)
            menu[item_id]["is_sold_out"] = not current_status
            save_menu(menu)
            return jsonify({"success": True, "is_sold_out": menu[item_id]["is_sold_out"]})

        return jsonify({"success": False, "message": "找不到該品項"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/order", methods=["POST"])
def place_order():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"success": False, "message": "無效資料"}), 400

        raw_items = data.get("items", data.get("food_list", []))
        safe_item_list = []
        
        if isinstance(raw_items, list):
            for item in raw_items:
                if isinstance(item, dict):
                    safe_item_list.append({
                        "name": str(item.get("name", "未知餐點")),
                        "price": int(item.get("price", 0)),
                        "quantity": int(item.get("quantity", 1)),
                    })

        phone = str(data.get("phone", "0000000000"))
        phone_last4 = phone[-4:] if len(phone) >= 4 else "0000"

        new_order = {
            "id": str(int(time.time() * 1000)),
            "table": str(data.get("table", "1")),
            "phone": phone,
            "phone_last4": phone_last4,
            "food_list": safe_item_list,
            "total": int(data.get("total", 0)),
        }

        ORDERS.append(new_order)
        return jsonify({"success": True, "message": "ok"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/order/accept", methods=["POST"])
def accept_order():
    try:
        data = request.get_json(silent=True)
        if not data or "order_id" not in data:
            return jsonify({"success": False, "message": "無效的訂單編號"}), 400

        target_id = str(data["order_id"])
        found_order = None
        for i, order in enumerate(ORDERS):
            if str(order.get("id")) == target_id:
                found_order = ORDERS.pop(i)
                break

        if found_order:
            ACCEPTED_ORDERS.append(found_order)
            return jsonify({"success": True})

        return jsonify({"success": False, "message": "找不到該筆訂單"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/order/complete", methods=["POST"])
def complete_order():
    try:
        data = request.get_json(silent=True)
        if not data or "order_id" not in data:
            return jsonify({"success": False, "message": "無效的訂單編號"}), 400

        target_id = str(data["order_id"])
        found_order = None
        for i, order in enumerate(ACCEPTED_ORDERS):
            if str(order.get("id")) == target_id:
                found_order = ACCEPTED_ORDERS.pop(i)
                break

        if found_order:
            COMPLETED_ORDERS.append(found_order)
            return jsonify({"success": True})

        return jsonify({"success": False, "message": "找不到該筆訂單"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
