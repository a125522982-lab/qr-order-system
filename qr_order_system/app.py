import json
import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MENU_FILE = "menu.json"

# 預設菜單
default_menu = {
    "1": {"name": "招牌牛肉麵", "price": 180},
    "2": {"name": "黃金排骨飯", "price": 150},
    "3": {"name": "手工水餃", "price": 80},
}

# 暫存訂單
ORDERS = []


def load_menu():
    if not os.path.exists(MENU_FILE):
        with open(MENU_FILE, "w", encoding="utf-8") as f:
            json.dump(default_menu, f, ensure_ascii=False, indent=4)
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@app.route("/")
def index():
    return '<h1>QR Code 點餐系統</h1><p><a href="/menu?table=1">前往 1 號桌點餐</a> | <a href="/admin">前往後台</a></p>'


@app.route("/menu")
def customer_menu():
    table = request.args.get("table", "1")
    return render_template("customer.html", table=table, menu=load_menu())


@app.route("/admin")
def admin_page():
    return render_template("admin.html", menu=load_menu(), orders=ORDERS)


@app.route("/api/menu", methods=["GET", "POST"])
def handle_menu():
    if request.method == "POST":
        data = request.json
        if data:
            with open(MENU_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return jsonify({"success": True})
        return jsonify({"success": False}), 400
    return jsonify(load_menu())


@app.route("/api/order", methods=["POST"])
def place_order():
  try:
    # 不使用會挑剔格式的 get_json，改用抓取最原始的位元資料
    raw_data = request.data
    if not raw_data:
      return jsonify({"success": False, "message": "沒有收到資料"}), 400

    # 手動用 json 模組解析
    data = json.loads(raw_data.decode("utf-8"))

    table = data.get("table", "1")
    items = data.get("items", [])
    total = data.get("total", 0)

    # 存入全域變數
    new_order = {"table": table, "items": items, "total": total}
    ORDERS.append(new_order)
    print("成功收到訂單:", new_order)

    return jsonify({"success": True, "message": "訂單送出成功！"})
  except Exception as e:
    # 就算有任何未預期的錯，也會安全回傳 JSON 格式而不是網頁 500 錯誤
    print("發生嚴重例外錯誤:", str(e))
    return jsonify(
        {"success": False, "message": f"伺服器處理發生異常: {str(e)}"}
    ), 500
if __name__ == "__main__":
    app.run(debug=True)
