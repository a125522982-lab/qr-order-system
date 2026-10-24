import json
import os
import socket
import time
from functools import wraps
from datetime import datetime, timezone, timedelta
from flask import Flask, jsonify, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "kukes_secret_key_0522_love"

ADMIN_USERNAME = "酷嗑斯"
ADMIN_PASSWORD = "0522love"

MENU_FILE = "menu.json"
HOURS_FILE = "hours.json"
ORDERS_FILE = "orders.json"

PRINTER_IP = "192.168.1.200"
PRINTER_PORT = 9100

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
    "301": {"name": "切達起司雞翅 (3)", "price": 120, "category": "cheese", "is_sold_out": False},
    "302": {"name": "切達起司雞里肌 (3)", "price": 70, "category": "cheese", "is_sold_out": False},
    "303": {"name": "切達起司脆皮香雞排", "price": 95, "category": "cheese", "is_sold_out": False},
    "304": {"name": "切達起司無骨雞腿排", "price": 110, "category": "cheese", "is_sold_out": False},
    "305": {"name": "切達起司嗑嗑雞丁", "price": 85, "category": "cheese", "is_sold_out": False},
    "306": {"name": "切達起司脆薯", "price": 65, "category": "cheese", "is_sold_out": False},
    "401": {"name": "香檸雞翅 (3)", "price": 120, "category": "lemon", "is_sold_out": False},
    "402": {"name": "香檸雞里肌 (3)", "price": 70, "category": "lemon", "is_sold_out": False},
    "403": {"name": "香檸脆皮香雞排", "price": 95, "category": "lemon", "is_sold_out": False},
    "404": {"name": "香檸無骨雞腿排", "price": 110, "category": "lemon", "is_sold_out": False},
    "405": {"name": "香檸嗑嗑雞丁", "price": 85, "category": "lemon", "is_sold_out": False},
    "501": {"name": "可樂 (250c.c)", "price": 20, "category": "drink", "is_sold_out": False},
    "502": {"name": "雪碧 (250c.c)", "price": 20, "category": "drink", "is_sold_out": False},
    "503": {"name": "芬達 (250c.c)", "price": 20, "category": "drink", "is_sold_out": False},
    "504": {"name": "可樂 (330c.c)", "price": 25, "category": "drink", "is_sold_out": False},
    "505": {"name": "雪碧 (330c.c)", "price": 25, "category": "drink", "is_sold_out": False},
    "506": {"name": "芬達 (330c.c)", "price": 25, "category": "drink", "is_sold_out": False},
    "507": {"name": "檸檬紅茶 (350c.c)", "price": 25, "category": "drink", "is_sold_out": False},
    "508": {"name": "原翠玉露 (580c.c)", "price": 30, "category": "drink", "is_sold_out": False},
}

default_hours = {
    "force_close": False,
    "Mon": {"open": "11:30", "close": "19:30", "enabled": False},
    "Tue": {"open": "11:30", "close": "19:30", "enabled": False},
    "Wed": {"open": "11:30", "close": "19:30", "enabled": True},
    "Thu": {"open": "11:30", "close": "19:30", "enabled": True},
    "Fri": {"open": "11:30", "close": "21:30", "enabled": True},
    "Sat": {"open": "11:30", "close": "21:30", "enabled": True},
    "Sun": {"open": "11:30", "close": "20:00", "enabled": True},
}

def load_json_file(filename, default_val):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(default_val, f, ensure_ascii=False, indent=4)
        return default_val
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default_val

def save_json_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_menu(): return load_json_file(MENU_FILE, default_menu)
def save_menu(menu_data): save_json_file(MENU_FILE, menu_data)
def load_hours(): return load_json_file(HOURS_FILE, default_hours)
def save_hours(hours_data): save_json_file(HOURS_FILE, hours_data)

def load_orders_db():
    data = load_json_file(ORDERS_FILE, {
        "ORDERS": [], 
        "ACCEPTED_ORDERS": [], 
        "COMPLETED_ORDERS": [], 
        "CANCELLED_ORDERS": [],
        "MEMBERS": {}
    })
    return (
        data.get("ORDERS", []),
        data.get("ACCEPTED_ORDERS", []),
        data.get("COMPLETED_ORDERS", []),
        data.get("CANCELLED_ORDERS", []),
        data.get("MEMBERS", {})
    )

def save_orders_db():
    data = {
        "ORDERS": ORDERS,
        "ACCEPTED_ORDERS": ACCEPTED_ORDERS,
        "COMPLETED_ORDERS": COMPLETED_ORDERS,
        "CANCELLED_ORDERS": CANCELLED_ORDERS,
        "MEMBERS": MEMBERS_DB
    }
    save_json_file(ORDERS_FILE, data)

ORDERS, ACCEPTED_ORDERS, COMPLETED_ORDERS, CANCELLED_ORDERS, MEMBERS_DB = load_orders_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def register_or_update_member(phone, total_spent_delta, created_at_str):
    phone = str(phone).strip()
    if len(phone) != 10: return
    if phone not in MEMBERS_DB:
        MEMBERS_DB[phone] = {
            "phone": phone,
            "first_seen": created_at_str,
            "order_count": 0,
            "total_spent": 0
        }
    MEMBERS_DB[phone]["order_count"] += 1
    MEMBERS_DB[phone]["total_spent"] += int(total_spent_delta)
    save_orders_db()

def get_customer_order_count(phone):
    phone_str = str(phone)
    if phone_str in MEMBERS_DB:
        return MEMBERS_DB[phone_str]["order_count"]
    return 0

def is_currently_open(hours_data=None):
    if hours_data is None: hours_data = load_hours()
    if hours_data.get("force_close"): return False

    taiwan_tz = timezone(timedelta(hours=8))
    now = datetime.now(taiwan_tz)
    days_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day_key = days_map[now.weekday()]
    
    day_config = hours_data.get(day_key, {})
    if not day_config.get("enabled"): return False
        
    try:
        open_time = datetime.strptime(day_config.get("open", "11:30"), "%H:%M").time()
        close_time = datetime.strptime(day_config.get("close", "20:00"), "%H:%M").time()
        return open_time <= now.time() <= close_time
    except Exception:
        return True

@app.route("/")
def index():
    return '<h1>酷嗑斯美式炸雞</h1><p><a href="/menu?table=1">前往點餐</a> | <a href="/admin">後台</a></p>'

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin_page"))
        else:
            error = "帳號或密碼錯誤！"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/menu")
def customer_menu():
    table = request.args.get("table", "1")
    return render_template("customer.html", table=table, menu=load_menu(), hours=load_hours())

@app.route("/api/hours", methods=["GET"])
def get_hours_api(): return jsonify(load_hours())

@app.route("/admin")
@login_required
def admin_page():
    taiwan_tz = timezone(timedelta(hours=8))
    today_str = datetime.now(taiwan_tz).strftime("%Y-%m-%d")
    selected_date = request.args.get("date", today_str)

    def filter_by_date(order_list):
        result = []
        for o in order_list:
            d_str = o.get("date_key")
            if not d_str and o.get("created_at"):
                d_str = o.get("created_at").split(" ")[0]
            if d_str == selected_date:
                o["order_count"] = get_customer_order_count(o.get("phone"))
                result.append(o)
        return result

    filtered_completed = filter_by_date(COMPLETED_ORDERS)
    filtered_cancelled = filter_by_date(CANCELLED_ORDERS)

    item_stats = {}
    for o in filtered_completed:
        for item in o.get("food_list", []):
            name = item.get("name", "未知品項")
            qty = item.get("quantity", 1)
            item_stats[name] = item_stats.get(name, 0) + qty

    def attach_order_count(order_list):
        for o in order_list:
            o["order_count"] = get_customer_order_count(o.get("phone"))
        return order_list

    members_list = list(MEMBERS_DB.values())
    members_list.sort(key=lambda x: x["order_count"], reverse=True)

    return render_template(
        "admin.html",
        menu=load_menu(),
        hours=load_hours(),
        orders=attach_order_count(list(ORDERS)),
        accepted_orders=attach_order_count(list(ACCEPTED_ORDERS)),
        completed_orders=filtered_completed,
        cancelled_orders=filtered_cancelled,
        members=members_list,
        total_revenue=sum(o.get("total", 0) for o in filtered_completed),
        item_stats=item_stats,
        selected_date=selected_date,
        today_str=today_str
    )

@app.route("/api/admin/check_orders", methods=["GET"])
@login_required
def api_check_orders(): return jsonify({"pending_count": len(ORDERS)})

@app.route("/api/hours/save", methods=["POST"])
@login_required
def update_hours():
    try:
        data = request.get_json(silent=True)
        if data and isinstance(data, dict):
            save_hours(data)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "無效資料"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/menu/toggle_soldout", methods=["POST"])
@login_required
def toggle_soldout():
    try:
        data = request.get_json(silent=True)
        item_id = str(data.get("item_id", ""))
        menu = load_menu()
        if item_id in menu:
            menu[item_id]["is_sold_out"] = not menu[item_id].get("is_sold_out", False)
            save_menu(menu)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "找不到該品項"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/promo/add", methods=["POST"])
@login_required
def add_promo_item():
    try:
        data = request.get_json(silent=True)
        if not data or not data.get("name") or not data.get("price"):
            return jsonify({"success": False, "message": "請輸入完整名稱與金額"}), 400

        menu = load_menu()
        promo_id = "promo_" + str(int(time.time()))
        menu[promo_id] = {
            "name": data["name"],
            "price": int(data["price"]),
            "category": "promo",
            "is_sold_out": False
        }
        save_menu(menu)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/promo/delete", methods=["POST"])
@login_required
def delete_promo_item():
    try:
        data = request.get_json(silent=True)
        if not data or not data.get("item_id"):
            return jsonify({"success": False, "message": "無效項目"}), 400

        item_id = str(data["item_id"])
        menu = load_menu()
        if item_id in menu:
            del menu[item_id]
            save_menu(menu)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "找不到該優惠品項"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/order", methods=["POST"])
def place_order():
    try:
        if not is_currently_open():
            return jsonify({"success": False, "message": "目前為非營業時間或已打烊，暫停線上點餐！"}), 403

        data = request.get_json(force=True, silent=True)
        if not data: return jsonify({"success": False, "message": "無效資料"}), 400

        order_id = str(int(time.time() * 1000))
        phone = str(data.get("phone", "0000000000")).strip()
        booking_time = data.get("booking_time", "").strip()
        
        taiwan_timezone = timezone(timedelta(hours=8))
        now_dt = datetime.now(taiwan_timezone)
        date_key = now_dt.strftime("%Y-%m-%d")
        now_str = now_dt.strftime("%Y-%m-%d %H:%M")
        
        order_type = "預約單" if booking_time else "即時單"
        est_time_display = f"預約 {booking_time} 取餐" if booking_time else "等待店家確認等候時間..."
        total_amount = int(data.get("total", 0))

        new_order = {
            "id": order_id,
            "table": str(data.get("table", "1")),
            "phone": phone,
            "phone_last4": phone[-4:],
            "food_list": data.get("items", []),
            "total": total_amount,
            "status": "pending",
            "order_type": order_type,
            "booking_time": booking_time,
            "est_time": est_time_display,
            "target_timestamp": 0,
            "created_at": now_str,
            "date_key": date_key
        }

        ORDERS.append(new_order)
        register_or_update_member(phone, total_amount, now_str)
        save_orders_db()
        return jsonify({"success": True, "order_id": order_id})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/order/status", methods=["GET"])
def check_order_status():
    order_id = request.args.get("order_id")
    phone = request.args.get("phone")
    phone_last4 = request.args.get("phone_last4")
    all_orders = ORDERS + ACCEPTED_ORDERS + COMPLETED_ORDERS + CANCELLED_ORDERS
    
    if order_id:
        for o in all_orders:
            if str(o.get("id")) == str(order_id):
                return jsonify({"success": True, "order": o})

    if phone:
        matched = [o for o in all_orders if str(o.get("phone")) == str(phone)]
        if matched:
            matched_sorted = sorted(matched, key=lambda x: str(x.get("id", "")), reverse=True)
            return jsonify({"success": True, "orders": matched_sorted})

    if phone_last4:
        matched = [o for o in all_orders if str(o.get("phone_last4")) == str(phone_last4)]
        if matched:
            matched_sorted = sorted(matched, key=lambda x: str(x.get("id", "")), reverse=True)
            return jsonify({"success": True, "orders": matched_sorted})
                
    return jsonify({"success": False}), 404

@app.route("/api/order/accept", methods=["POST"])
@login_required
def accept_order():
    data = request.get_json(silent=True) or {}
    target_id = str(data.get("order_id", ""))
    est_minutes = int(data.get("est_minutes", 15))
    
    for i, order in enumerate(ORDERS):
        if str(order.get("id")) == target_id:
            found = ORDERS.pop(i)
            found["status"] = "accepted"
            
            if found["order_type"] == "即時單":
                target_ts = time.time() + (est_minutes * 60)
                found["target_timestamp"] = target_ts
                found["est_time"] = f"{est_minutes}分鐘"
            else:
                found["est_time"] = f"預約 {found['booking_time']} 取餐"
            
            ACCEPTED_ORDERS.append(found)
            save_orders_db()
            
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((PRINTER_IP, PRINTER_PORT))
                print_data = b"\x1b\x40" + f"酷嗑斯美式炸雞 [{found['order_type']}]\n桌號: {found['table']}\n電話: {found['phone']}\n取餐末四碼: {found['phone_last4']}\n時間: {found.get('created_at','')}\n".encode("big5", errors="ignore")
                if found['booking_time']:
                    print_data += f"預約取餐: {found['booking_time']}\n".encode("big5", errors="ignore")
                for item in found['food_list']:
                    print_data += f"{item['name']} x {item['quantity']}\n".encode("big5", errors="ignore")
                print_data += f"總計: ${found['total']}\n\n\n\x1d\x56\x42\x00".encode("big5", errors="ignore")
                s.sendall(print_data)
                s.close()
            except Exception:
                pass
            return jsonify({"success": True})
            
    return jsonify({"success": False}), 404

@app.route("/api/order/acknowledge", methods=["POST"])
def acknowledge_order():
    data = request.get_json(silent=True) or {}
    target_id = str(data.get("order_id", ""))
    for order in ACCEPTED_ORDERS:
        if str(order.get("id")) == target_id:
            order["status"] = "acknowledged"
            save_orders_db()
            return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route("/api/order/ready", methods=["POST"])
@login_required
def ready_order():
    data = request.get_json(silent=True) or {}
    target_id = str(data.get("order_id", ""))
    for order in ACCEPTED_ORDERS:
        if str(order.get("id")) == target_id:
            order["status"] = "ready"
            save_orders_db()
            return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route("/api/order/complete", methods=["POST"])
def complete_order():
    data = request.get_json(silent=True) or {}
    target_id = str(data.get("order_id", ""))
    for i, order in enumerate(ACCEPTED_ORDERS):
        if str(order.get("id")) == target_id:
            found = ACCEPTED_ORDERS.pop(i)
            found["status"] = "completed"
            COMPLETED_ORDERS.append(found)
            save_orders_db()
            return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route("/api/order/cancel", methods=["POST"])
def cancel_order():
    data = request.get_json(silent=True) or {}
    target_id = str(data.get("order_id", ""))
    for lst in [ORDERS, ACCEPTED_ORDERS]:
        for i, order in enumerate(lst):
            if str(order.get("id")) == target_id:
                found = lst.pop(i)
                found["status"] = "cancelled"
                CANCELLED_ORDERS.append(found)
                phone_str = str(found.get("phone", ""))
                if phone_str in MEMBERS_DB:
                    MEMBERS_DB[phone_str]["order_count"] = max(0, MEMBERS_DB[phone_str]["order_count"] - 1)
                    MEMBERS_DB[phone_str]["total_spent"] = max(0, MEMBERS_DB[phone_str]["total_spent"] - int(found.get("total", 0)))
                save_orders_db()
                return jsonify({"success": True})
    return jsonify({"success": False}), 404

# 🔥 新增：手動刪除歷史訂單功能
@app.route("/api/admin/delete_order", methods=["POST"])
@login_required
def delete_order():
    try:
        data = request.get_json(silent=True) or {}
        target_id = str(data.get("order_id", ""))
        for lst in [COMPLETED_ORDERS, CANCELLED_ORDERS]:
            for i, order in enumerate(lst):
                if str(order.get("id")) == target_id:
                    lst.pop(i)
                    save_orders_db()
                    return jsonify({"success": True})
        return jsonify({"success": False, "message": "找不到該訂單"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# 🔥 新增：手動刪除會員資料功能
@app.route("/api/admin/delete_member", methods=["POST"])
@login_required
def delete_member():
    try:
        data = request.get_json(silent=True) or {}
        phone = str(data.get("phone", "")).strip()
        if phone in MEMBERS_DB:
            del MEMBERS_DB[phone]
            save_orders_db()
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "找不到該會員"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
