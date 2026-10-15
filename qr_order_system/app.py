import json
import os
import time
from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MENU_FILE = "menu.json"
HOURS_FILE = "hours.json"

default_menu = {
    "101": {"name": "無骨雞腿排", "price": 90, "category": "fried", "is_sold_out": False},
    "102": {"name": "脆皮香雞排", "price": 75, "category": "fried", "is_sold_out": False},
    "103": {"name": "雞腿", "price": 55, "category": "fried", "is_sold_out": False},
    "104": {"name": "雞塊", "price": 55, "category": "fried", "is_sold_out": False},
    "105": {"name": "雞翅", "price": 35, "category": "fried", "is_sold_out": False},
    "106": {"name": "乳酪棒 (4)", "price": 50, "category": "fried", "is_sold_out": False},
    "107": {"name": "芋泥球 (8)", "price": 50, "category": "fried", "is_sold_out": False},
    "108": {"name": "起司球 (4)", "price": 50, "category": "fried", "is_sold_out": False},
    "109": {"name": "甜不辣", "price": 35, "category": "fried", "is_sold_out": False},
    "110": {"name": "百頁豆腐", "price": 30, "category": "fried", "is_sold_out": False},
    "111": {"name": "米血 (6)", "price": 30, "category": "fried", "is_sold_out": False},
    "112": {"name": "帶皮薯瓣", "price": 60, "category": "fried", "is_sold_out": False},
    "113": {"name": "杏鮑菇", "price": 55, "category": "fried", "is_sold_out": False},
    "114": {"name": "深海鱈魚條 (2)", "price": 40, "category": "fried", "is_sold_out": False},
    "115": {"name": "娘惹山藥捲 (4)", "price": 40, "category": "fried", "is_sold_out": False},
    "116": {"name": "雞軟骨", "price": 60, "category": "fried", "is_sold_out": False},
    "117": {"name": "魷米花", "price": 60, "category": "fried", "is_sold_out": False},
    "118": {"name": "嗑嗑雞丁", "price": 65, "category": "fried", "is_sold_out": False},
    "119": {"name": "雞皮", "price": 40, "category": "fried", "is_sold_out": False},
    "120": {"name": "美式脆薯", "price": 45, "category": "fried", "is_sold_out": False},
    "121": {"name": "薯餅 (4)", "price": 40, "category": "fried", "is_sold_out": False},
    "122": {"name": "花枝丸 (5)", "price": 40, "category": "fried", "is_sold_out": False},
    "123": {"name": "麥嗑雞塊 (5)", "price": 45, "category": "fried", "is_sold_out": False},
    "124": {"name": "洋蔥圈 (6)", "price": 40, "category": "fried", "is_sold_out": False},
    "125": {"name": "煉香花月圓", "price": 40, "category": "fried", "is_sold_out": False},
    "126": {"name": "煉乳銀絲卷 (4)", "price": 40, "category": "fried", "is_sold_out": False},
    "127": {"name": "椒鹽銀絲卷 (4)", "price": 30, "category": "fried", "is_sold_out": False},
    "128": {"name": "黃金地瓜條", "price": 50, "category": "fried", "is_sold_out": False},
    "129": {"name": "起司薯球 (6)", "price": 50, "category": "fried", "is_sold_out": False},
    "201": {"name": "1號餐 (雞翅+雞塊+飲料)", "price": 100, "category": "combo", "is_sold_out": False},
    "202": {"name": "2號餐 (雞塊+雞腿+飲料)", "price": 120, "category": "combo", "is_sold_out": False},
    "203": {"name": "3號餐 (美式脆薯+嗑嗑雞丁+麥嗑雞塊+飲料)", "price": 140, "category": "combo", "is_sold_out": False},
    "204": {"name": "4號餐 (雞腿+雞塊+雞翅+飲料)", "price": 155, "category": "combo", "is_sold_out": False},
    "205": {"name": "5號餐 (雞排+美式脆薯+飲料)", "price": 125, "category": "combo", "is_sold_out": False},
    "206": {"name": "全家桶", "price": 339, "category": "bucket", "is_sold_out": False},
    "207": {"name": "超值全家桶", "price": 449, "category": "bucket", "is_sold_out": False},
    "208": {"name": "炸全雞", "price": 429, "category": "bucket", "is_sold_out": False},
    "209": {"name": "全雞餐", "price": 579, "category": "bucket", "is_sold_out": False},
    "210": {"name": "雞翅滿足桶", "price": 399, "category": "bucket", "is_sold_out": False},
    "211": {"name": "雞塊滿足桶", "price": 399, "category": "bucket", "is_sold_out": False},
    "212": {"name": "雞腿滿足桶", "price": 399, "category": "bucket", "is_sold_out": False},
}

default_hours = {
    "force_close": False,
    "Mon": {"open": "11:00", "close": "22:00", "enabled": True},
    "Tue": {"open": "11:00", "close": "22:00", "enabled": True},
    "Wed": {"open": "11:00", "close": "22:00", "enabled": True},
    "Thu": {"open": "11:00", "close": "22:00", "enabled": True},
    "Fri": {"open": "11:00", "close": "23:00", "enabled": True},
    "Sat": {"open": "11:00", "close": "23:00", "enabled": True},
    "Sun": {"open": "11:00", "close": "22:00", "enabled": True},
}

ORDERS = []
ACCEPTED_ORDERS = []
COMPLETED_ORDERS = []
CANCELLED_ORDERS = []


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
                    if "category" not in item_info:
                        item_info["category"] = "fried"
                return data
    except Exception:
        pass
    return default_menu


def save_menu(menu_data):
    with open(MENU_FILE, "w", encoding="utf-8") as f:
        json.dump(menu_data, f, ensure_ascii=False, indent=4)


def load_hours():
    if not os.path.exists(HOURS_FILE):
        with open(HOURS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_hours, f, ensure_ascii=False, indent=4)
    try:
        with open(HOURS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data and isinstance(data, dict):
                if "force_close" not in data:
                    data["force_close"] = False
                return data
    except Exception:
        pass
    return default_hours


def save_hours(hours_data):
    with open(HOURS_FILE, "w", encoding="utf-8") as f:
        json.dump(hours_data, f, ensure_ascii=False, indent=4)


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
    hours = load_hours()
    
    force_close = bool(hours.get("force_close", False))
    
    if force_close:
        is_open = False
        display_hours = {"open": "暫停", "close": "休息中"}
    else:
        now = datetime.now()
        day_map = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
        today_key = day_map[now.weekday()]
        today_setting = hours.get(today_key, {"enabled": True, "open": "11:00", "close": "22:00"})
        
        is_open = True
        if not today_setting.get("enabled", True):
            is_open = False
        else:
            current_time_str = now.strftime("%H:%M")
            open_time = today_setting.get("open", "00:00")
            close_time = today_setting.get("close", "24:00")
            if not (open_time <= current_time_str <= close_time):
                is_open = False
        display_hours = today_setting

    return render_template("customer.html", table=table, menu=load_menu(), is_open=is_open, hours=display_hours)


@app.route("/admin")
def admin_page():
    global ORDERS, ACCEPTED_ORDERS, COMPLETED_ORDERS, CANCELLED_ORDERS
    current_menu = load_menu()
    current_hours = load_hours()
    
    def clean_list(lst, status):
        cleaned = []
        for o in lst:
            if isinstance(o, dict) and callable(o.get("food_list")) is False:
                fl = o.get("food_list", [])
                if isinstance(fl, list):
                    phone = str(o.get("phone", "0000000000"))
                    phone_last4 = phone[-4:] if len(phone) >= 4 else "0000"
                    cleaned.append({
                        "id": str(o.get("id", time.time())),
                        "table": str(o.get("table", "1")),
                        "phone": phone,
                        "phone_last4": phone_last4,
                        "food_list": fl,
                        "total": int(o.get("total", 0)),
                        "status": status,
                        "est_time": str(o.get("est_time", "")),
                        "spicy": str(o.get("spicy", "不辣")),
                        "pepper": str(o.get("pepper", "要"))
                    })
        return cleaned

    ORDERS = clean_list(ORDERS, "pending")
    ACCEPTED_ORDERS = clean_list(ACCEPTED_ORDERS, "accepted")
    COMPLETED_ORDERS = clean_list(COMPLETED_ORDERS, "completed")
    CANCELLED_ORDERS = clean_list(CANCELLED_ORDERS, "cancelled")

    total_revenue = sum(o["total"] for o in COMPLETED_ORDERS)
    item_stats = {}
    for o in COMPLETED_ORDERS:
        for item in o["food_list"]:
            name = item["name"]
            qty = int(item.get("quantity", 1))
            item_stats[name] = item_stats.get(name, 0) + qty

    return render_template(
        "admin.html",
        menu=current_menu,
        hours=current_hours,
        orders=ORDERS,
        accepted_orders=ACCEPTED_ORDERS,
        completed_orders=COMPLETED_ORDERS,
        cancelled_orders=CANCELLED_ORDERS,
        total_revenue=total_revenue,
        item_stats=item_stats
    )


@app.route("/api/hours/save", methods=["POST"])
def update_hours():
    try:
        data = request.get_json(silent=True)
        if data and isinstance(data, dict):
            # 明確確保從前端接收到的 force_close 轉為正確的布林值儲存
            data["force_close"] = True if data.get("force_close") == True or data.get("force_close") == "true" else False
            save_hours(data)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "無效資料"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/order/status", methods=["GET"])
def check_order_status():
    order_id = request.args.get("order_id")
    phone_last4 = request.args.get("phone_last4")
    
    all_orders = ORDERS + ACCEPTED_ORDERS + COMPLETED_ORDERS + CANCELLED_ORDERS
    
    if order_id:
        for o in all_orders:
            if str(o.get("id")) == str(order_id):
                return jsonify({"success": True, "order": o})
                
    if phone_last4:
        for o in reversed(all_orders):
            if str(o.get("phone_last4")) == str(phone_last4) and o.get("status") in ["pending", "accepted", "completed"]:
                return jsonify({"success": True, "order": o})
                
    return jsonify({"success": False, "message": "找不到相關訂單"}), 404


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
        order_id = str(int(time.time() * 1000))

        new_order = {
            "id": order_id,
            "table": str(data.get("table", "1")),
            "phone": phone,
            "phone_last4": phone_last4,
            "food_list": safe_item_list,
            "total": int(data.get("total", 0)),
            "status": "pending",
            "est_time": "",
            "spicy": str(data.get("spicy", "不辣")),
            "pepper": str(data.get("pepper", "要"))
        }

        ORDERS.append(new_order)
        return jsonify({"success": True, "order_id": order_id, "message": "ok"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/order/accept", methods=["POST"])
def accept_order():
    try:
        data = request.get_json(silent=True)
        if not data or "order_id" not in data:
            return jsonify({"success": False, "message": "無效的訂單編號"}), 400

        target_id = str(data["order_id"])
        est_time = str(data.get("est_time", "15分鐘"))
        
        found_order = None
        for i, order in enumerate(ORDERS):
            if str(order.get("id")) == target_id:
                found_order = ORDERS.pop(i)
                found_order["status"] = "accepted"
                found_order["est_time"] = est_time
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
                found_order["status"] = "completed"
                break

        if found_order:
            COMPLETED_ORDERS.append(found_order)
            return jsonify({"success": True})

        return jsonify({"success": False, "message": "找不到該筆訂單"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/order/cancel", methods=["POST"])
def cancel_order():
    try:
        data = request.get_json(silent=True)
        if not data or "order_id" not in data:
            return jsonify({"success": False, "message": "無效的訂單編號"}), 4
