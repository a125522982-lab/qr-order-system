import json
import os
import socket
import time
from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MENU_FILE = "menu.json"
HOURS_FILE = "hours.json"

PRINTER_IP = "192.168.1.100"
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
            return json.load(f)
    except Exception:
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
            return json.load(f)
    except Exception:
        return default_hours


def save_hours(hours_data):
    with open(HOURS_FILE, "w", encoding="utf-8") as f:
        json.dump(hours_data, f, ensure_ascii=False, indent=4)


def check_is_open(hours_data):
    # 1. 若手動勾選強制打烊，直接不開放點餐
    if hours_data.get("force_close", False):
        return False
    
    # 2. 判斷當天星期與時間
    weekday_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    now = datetime.now()
    today_key = weekday_map[now.weekday()]
    today_rule = hours_data.get(today_key, {})
    
    # 若當日未開啟營業
    if not today_rule.get("enabled", False):
        return False
        
    open_str = today_rule.get("open", "").strip()
    close_str = today_rule.get("close", "").strip()
    
    if not open_str or not close_str:
        return True  # 未指定時間則預設開放
        
    try:
        open_time = datetime.strptime(open_str, "%H:%M").time()
        close_time = datetime.strptime(close_str, "%H:%M").time()
        now_time = now.time()
        
        if open_time <= close_time:
            return open_time <= now_time <= close_time
        else:
            # 跨夜營業（例如 18:00 到 02:00）
            return now_time >= open_time or now_time <= close_time
    except Exception:
        return True


@app.route("/")
def index():
    return '<h1>酷嗑斯美式炸雞</h1><p><a href="/menu?table=1">前往點餐</a> | <a href="/admin">後台</a></p>'


@app.route("/menu")
def customer_menu():
    table = request.args.get("table", "1")
    menu = load_menu()
    hours = load_hours()
    is_open = check_is_open(hours)
    return render_template("customer.html", table=table, menu=menu, is_open=is_open)


@app.route("/admin")
def admin_page():
    return render_template(
        "admin.html",
        menu=load_menu(),
        hours=load_hours(),
        orders=ORDERS,
        accepted_orders=ACCEPTED_ORDERS,
        completed_orders=COMPLETED_ORDERS,
        cancelled_orders=CANCELLED_ORDERS,
        total_revenue=sum(o.get("total", 0) for o in COMPLETED_ORDERS),
        item_stats={}
    )


# --- 營業時間儲存 API ---
@app.route("/api/hours/save", methods=["POST"])
def update_hours():
    try:
        data = request.get_json(silent=True)
        if data and isinstance(data, dict):
            save_hours(data)
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "無效資料"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# --- 菜單售罄切換 API ---
@app.route("/api/menu/toggle_soldout", methods=["POST"])
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
