# ============================================
# 第5课：表单处理——GET vs POST
# 运行：python lessons/05_forms.py
# 访问：http://127.0.0.1:5000/guestbook
# ============================================

from flask import Flask, render_template, request

app = Flask(__name__, template_folder="../templates", static_folder="../static")

# 用 Python 列表暂存数据（刷新后就没了，第6课会解决）
messages = []


# ----- GET 和 POST 的区别 -----
# GET  : 浏览器向服务器"要"东西（打开页面、搜索参数在URL里）
# POST : 浏览器向服务器"发"东西（提交表单，数据在请求体里，URL上看不到）

@app.route("/guestbook", methods=["GET", "POST"])
def guestbook():
    if request.method == "POST":
        # POST 时：用户提交了表单，request.form 里是表单数据
        username = request.form.get("username", "匿名")
        message = request.form.get("message", "")
        messages.append({"username": username, "message": message})

    # GET 和 POST 都会走到这里：渲染页面 + 显示所有留言
    return render_template("guestbook.html", messages=messages)


# ----- 附加演示：GET 参数（URL问号后面的东西）-----
# 访问 /search?q=flask 试试
@app.route("/search")
def search():
    # request.args 获取 URL 中的查询参数
    keyword = request.args.get("q", "什么都没搜")
    return f"<h1>🔍 搜索：{keyword}</h1><p>（这是 GET 方式传参，参数在URL里可见）</p>"


if __name__ == "__main__":
    app.run(debug=True)


# ============================================
# 核心知识点：
#
# 1. methods=["GET", "POST"]
#    允许这个路由同时接受 GET 和 POST 请求
#    不指定时默认只有 GET
#
# 2. request.method
#    判断当前请求是 GET 还是 POST
#    GET  → 用户打开页面
#    POST → 用户提交表单
#
# 3. request.form.get("字段名", "默认值")
#    从 POST 表单中取数据
#    字段名对应 HTML 中 <input name="xxx">
#
# 4. request.args.get("参数名", "默认值")
#    从 URL 查询字符串中取数据
#    /search?q=flask  →  args["q"] == "flask"
#
# 5. GET vs POST 一句话：
#    GET  : 数据在URL里，看得见，适合搜索关键词、翻页
#    POST : 数据在请求体里，看不见，适合密码、长文本
# ============================================
