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

# 儲存訂單的記憶體資料庫
ORDERS = []


def load_menu():
  """讀取菜單檔案"""
  if not os.path.exists(MENU_FILE):
    save_menu(default_menu)
  with open(MENU_FILE, "r", encoding="utf-8") as f:
    return json.load(f)


def save_menu(menu_data):
  """儲存菜單到檔案"""
  with open(MENU_FILE, "w", encoding="utf-8") as f:
    json.dump(menu_data, f, ensure_ascii=False, indent=4)


# 1. 主頁面導向
@app.route("/")
def index():
  return (
      '<h1>QR Code 點餐系統</h1><p><a href="/menu?table=1">👉 點擊前往 1'
      ' 號桌點餐頁面</a></p><p><a href="/admin">👉 點擊前往店家後台管理</a></p>'
  )


# 2. 客人點餐頁面
@app.route("/menu")
def customer_menu():
  table = request.args.get("table", "1")
  current_menu = load_menu()
  return render_template("customer.html", table=table, menu=current_menu)


# 3. 店家後台管理頁面 (新增這段讓後台可以進去)
@app.route("/admin")
def admin_page():
  current_menu = load_menu()
  return render_template("admin.html", menu=current_menu, orders=ORDERS)


# 4. 取得/更新菜單的 API
@app.route("/api/menu", methods=["GET"])
def get_menu_api():
  return jsonify(load_menu())


@app.route("/api/menu", methods=["POST"])
def update_menu_api():
  data = request.json
  if data:
    save_menu(data)
    return jsonify({"success": True, "message": "菜單更新成功！"})
  return jsonify({"success": False, "message": "資料錯誤"}), 400


# 5. 接收客人口腹訂單的 API（已加入防呆機制）
@app.route("/api/order", methods=["POST"], endpoint="place_order_api")
def place_order():
  try:
    data = request.get_json(silent=True)
    if not data:
      return jsonify(
          {"success": False, "message": "無效的請求資料"}
      ), 400

    table = data.get("table", "未知桌號")
    items = data.get("items", [])
    total = data.get("total", 0)

    new_order = {"table": table, "items": items, "total": total}
    ORDERS.append(new_order)
    print(f"收到來自 {table} 號桌的新訂單：", new_order)

    return jsonify({"success": True, "message": "訂單送出成功！"})
  except Exception as e:
    print(f"處理訂單發生錯誤: {str(e)}")
    return jsonify(
        {"success": False, "message": f"伺服器內部錯誤: {str(e)}"}
    ), 500
if __name__ == "__main__":
  app.run(debug=True)
