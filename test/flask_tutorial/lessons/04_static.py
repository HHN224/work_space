# ============================================
# 第4课：静态文件——CSS、图片、JS 等"不会变的文件"
# 先确保第3课的服务器已关掉，然后运行：
#   python lessons/04_static.py
# ============================================

from flask import Flask, render_template

app = Flask(__name__, template_folder="../templates", static_folder="../static")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/todos")
def todos():
    tasks = ["学 Flask", "写项目", "部署上线"]
    return render_template("todo_list.html", todos=tasks)


if __name__ == "__main__":
    app.run(debug=True)


# ============================================
# 核心知识点：
#
# 1. static/ 目录 - Flask 默认从这里提供静态文件
#    CSS → static/style.css
#    图片 → static/logo.png
#    JS   → static/script.js
#
# 2. url_for('static', filename='xxx')
#    在模板中动态生成静态文件的URL
#    比直接写 /static/style.css 更好：
#    - 即使网站换个域名，路径仍然正确
#    - 将来上生产环境可以用 CDN 加速
#
# 3. static_folder="../static"
#    因为 .py 文件在 lessons/ 目录，需要指定到父级
# ============================================
