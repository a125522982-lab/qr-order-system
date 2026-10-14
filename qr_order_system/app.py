import json
import os
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

MENU_FILE = "menu.json"

# 預設菜單（如果檔案不存在就建立一個）
default_menu = {
    "1": {"name": "招牌牛肉麵", "price": 180},
    "2": {"name": "黃金排骨飯", "price": 150},
    "3": {"name": "手工水餃", "price": 80},
}


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


# 客人點餐頁面
@app.route("/menu")
def customer_menu():
  table = request.args.get("table", "1")
  current_menu = load_menu()  # 每次都重新讀取最新菜單
  return render_template("customer.html", table=table, menu=current_menu)


# 後台讀取菜單 API
@app.route("/api/menu", methods=["GET"])
def get_menu_api():
  return jsonify(load_menu())


# 後台修改/新增/刪除菜單的 API 範例
@app.route("/api/menu", methods=["POST"])
def update_menu_api():
  data = request.json  # 預期傳入整套新的菜單字典
  if data:
    save_menu(data)
    return jsonify({"success": True, "message": "菜單更新成功！"})
  return jsonify({"success": False, "message": "資料錯誤"}), 400


# 接收訂單的 API
@app.route("/api/order", methods=["POST"])
def place_order():
  data = request.json
  table = data.get("table")
  items = data.get("items")
  total = data.get("total")

  print(f"收到來自 {table} 號桌的新訂單：", items)
  return jsonify({"success": True, "message": "訂單送出成功！"})


if __name__ == "__main__":
  app.run(debug=True)
