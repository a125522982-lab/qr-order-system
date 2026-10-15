import json
import os
import time
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MENU_FILE = "menu.json"

# 將完整的「酷嗑斯美式炸雞」菜單直接寫死在此處，永不遺失
default_menu = {
    # 單點炸物系列
    "101": {"name": "無骨雞腿排", "price": 90},
    "102": {"name": "脆皮香雞排", "price": 75},
    "103": {"name": "雞腿", "price": 55},
    "104": {"name": "雞塊", "price": 55},
    "105": {"name": "雞翅", "price": 35},
    "106": {"name": "乳酪棒 (4)", "price": 50},
    "107": {"name": "芋泥球 (8)", "price": 50},
    "108": {"name": "起司球 (4)", "price": 50},
    "109": {"name": "甜不辣", "price": 35},
    "110": {"name": "百頁豆腐", "price": 30},
    "111": {"name": "米血 (6)", "price": 30},
    "112": {"name": "帶皮薯瓣", "price": 60},
    "113": {"name": "杏鮑菇", "price": 55},
    "114": {"name": "深海鱈魚條 (2)", "price": 40},
    "115": {"name": "娘惹山藥捲 (4)", "price": 40},
    "116": {"name": "雞軟骨", "price": 60},
    "117": {"name": "魷米花", "price": 60},
    "118": {"name": "嗑嗑雞丁", "price": 65},
    "119": {"name": "雞皮", "price": 40},
    "120": {"name": "美式脆薯", "price": 45},
    "121": {"name": "薯餅 (4)", "price": 40},
    "122": {"name": "花枝丸 (5)", "price": 40},
    "123": {"name": "麥嗑雞塊 (5)", "price": 45},
    "124": {"name": "洋蔥圈 (6)", "price": 40},
    "125": {"name": "煉香花月圓", "price": 40},
    "126": {"name": "煉乳銀絲卷 (4)", "price": 40},
    "127": {"name": "椒鹽銀絲卷 (4)", "price": 30},
    "128": {"name": "黃金地瓜條", "price": 50},
    "129": {"name": "起司薯球 (6)", "price": 50},

    # 套餐系列
    "201": {"name": "1號餐 (雞翅+雞塊+飲料)", "price": 100},
    "202": {"name": "2號餐 (雞塊+雞腿+飲料)", "price": 120},
    "203": {"name": "3號餐 (美式脆薯+嗑嗑雞丁+麥嗑雞塊+飲料)", "price": 140},
    "204": {"name": "4號餐 (雞腿+雞塊+雞翅+飲料)", "price": 155},
    "205": {"name": "5號餐 (雞排+美式脆薯+飲料)", "price": 125},
    "206": {"name": "全家桶 (3雞翅+3雞塊+2雞腿+美式脆薯+麥嗑雞塊+3飲料)", "price": 339},
    "207": {"name": "超值全家桶 (3雞翅+3雞塊+2雞腿+美式脆薯+麥嗑雞塊+3飲料+炸全雞)", "price": 449},
    "208": {"name": "炸全雞 (限量供應:番茄/香檸/起司)", "price": 429},
    "209": {"name": "全雞餐 (炸全雞+3罐飲料+小點心任選三樣)", "price": 579},
    "210": {"name": "雞翅滿足桶 (12支雞翅)", "price": 399},
    "211": {"name": "雞塊滿足桶 (8個雞塊)", "price": 399},
    "212": {"name": "雞腿滿足桶 (8支雞腿)", "price": 399},

    # 黃金切達起司系列
    "301": {"name": "切達起司雞翅 (3)", "price": 120},
    "302": {"name": "切達起司雞里肌 (3)", "price": 70},
    "303": {"name": "切達起司脆皮香雞排", "price": 95},
    "304": {"name": "切達起司無骨雞腿排", "price": 110},
    "305": {"name": "切達起司嗑嗑雞丁", "price": 85},
    "306": {"name": "切達起司脆薯", "price": 65},

    # 香檸風味系列
    "401": {"name": "香檸雞翅 (3)", "price": 120},
    "402": {"name": "香檸雞里肌 (3)", "price": 70},
    "403": {"name": "香檸脆皮香雞排", "price": 95},
    "404": {"name": "香檸無骨雞腿排", "price": 110},
    "405": {"name": "香檸嗑嗑雞丁", "price": 85}
}

ORDERS = []
COMPLETED_ORDERS = []


def load_menu():
    # 每次啟動時，若 menu.json 不存在或需要重置，直接以寫死的完整菜單建立
    if not os.path.exists(MENU_FILE):
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(default_menu, f, ensure_ascii=False, indent=4)
    try:
        with open(MENU_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # 確保讀出來的不是空的
            if data and isinstance(data, dict):
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
    global ORDERS, COMPLETED_ORDERS
    current_menu = load_menu()
    
    clean_orders = []
    for o in ORDERS:
        if isinstance(o, dict) and callable(o.get("food_list")) is False:
            fl = o.get("food_list", [])
            if isinstance(fl, list):
                clean_orders.append({
                    "id": str(o.get("id", time.time())),
                    "table": str(o.get("table", "1")),
                    "food_list": fl,
                    "total": int(o.get("total", 0))
                })
    ORDERS = clean_orders

    clean_completed = []
    for o in COMPLETED_ORDERS:
        if isinstance(o, dict):
            fl = o.get("food_list", [])
            if isinstance(fl, list):
                clean_completed.append({
                    "id": str(o.get("id", time.time())),
                    "table": str(o.get("table", "1")),
                    "food_list": fl,
                    "total": int(o.get("total", 0))
                })
    COMPLETED_ORDERS = clean_completed

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

        new_order = {
            "id": str(int(time.time() * 1000)),
            "table": str(data.get("table", "1")),
            "food_list": safe_item_list,
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
