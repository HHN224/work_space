# ============================================
# 第6课：Todo 待办事项应用（完整项目）
# 运行：python lessons/06_todo_app.py
# 访问：http://127.0.0.1:5000
#
# 功能：
#   ✅ 添加待办事项
#   ✅ 查看所有待办
#   ✅ 删除待办
#   ✅ 数据存 JSON 文件（重启不丢失）
# ============================================

import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder="../templates", static_folder="../static")

# 数据文件路径：data.json 放在项目根目录
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data.json")


# ----- 工具函数：读写 JSON 文件 -----
def load_todos():
    """从 JSON 文件加载待办列表"""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_todos(todos):
    """把待办列表写入 JSON 文件"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


# ----- 路由：展示待办 + 添加待办 -----
@app.route("/", methods=["GET", "POST"])
def index():
    todos = load_todos()

    if request.method == "POST":
        # 用户提交了新待办
        title = request.form.get("title", "").strip()
        if title:
            new_id = max([t["id"] for t in todos], default=0) + 1
            todos.append({
                "id": new_id,
                "title": title,
                "done": False
            })
            save_todos(todos)
        # POST 后重定向到 GET，避免刷新时重复提交
        return redirect(url_for("index"))

    return render_template("todo_app.html", todos=todos)


# ----- 路由：删除待办 -----
@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete_todo(todo_id):
    todos = load_todos()
    todos = [t for t in todos if t["id"] != todo_id]
    save_todos(todos)
    return redirect(url_for("index"))


# ----- 路由：标记完成/未完成 -----
@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle_todo(todo_id):
    todos = load_todos()
    for t in todos:
        if t["id"] == todo_id:
            t["done"] = not t["done"]
    save_todos(todos)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)


# ============================================
# 新知识点：
#
# 1. redirect(url_for("index"))
#    服务器告诉浏览器："请跳转到首页"
#    为什么？POST 后直接返回页面，用户刷新会重复提交
#    POST → 处理数据 → redirect → GET → 显示页面
#    这叫 PRG 模式（Post-Redirect-Get）
#
# 2. JSON 文件存储
#    json.load(f)   → 从文件读取 → Python 列表
#    json.dump(x,f) → Python 列表 → 写入文件
#    比数据库简单，适合小项目
#
# 3. 列表推导式删除
#    [t for t in todos if t["id"] != todo_id]
#    选出所有 id 不匹配的，等于删掉了那个 id
# ============================================
