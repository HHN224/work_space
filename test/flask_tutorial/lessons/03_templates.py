# ============================================
# 第3课：Jinja2 模板——让HTML和Python各司其职
# 运行：python lessons/03_templates.py
# 访问：
#   http://127.0.0.1:5000              → 模板继承演示
#   http://127.0.0.1:5000/about        → 模板继承演示
#   http://127.0.0.1:5000/simple        → 变量替换演示
#   http://127.0.0.1:5000/todos        → 条件判断 + 循环演示
# ============================================

from flask import Flask, render_template

app = Flask(__name__, template_folder="../templates")


# ----- 知识点1：render_template 渲染模板 -----
# render_template("文件名", 变量=值, ...)
# Flask 自动在项目根目录下的 templates/ 文件夹中寻找模板

@app.route("/simple")
def simple():
    return render_template(
        "simple.html",
        title="简单示例",
        heading="你好，Flask！",
        message="这是通过模板渲染出来的页面。"
    )


# ----- 知识点2：模板中的循环和条件判断 -----
# {% for item in list %} ... {% endfor %}   循环
# {% if condition %} ... {% endif %}       条件判断
# {{ variable }}                           输出变量值

@app.route("/todos")
def todos():
    tasks = ["学 Flask", "写项目", "部署上线"]
    return render_template("todo_list.html", todos=tasks)


# ----- 知识点3：模板继承（核心！）-----
# base.html 定义页面的公共骨架（导航栏、页脚）
# 子模板用 extends 继承，用 block 填充自己的内容
# 只需要写一次导航栏，所有页面都能用

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)


# ============================================
# Jinja2 语法速查：
#
# {{ 变量名 }}        输出变量的值（自动转义HTML，防止XSS攻击）
# {% if ... %}        条件判断
# {% for x in list %} 循环
# {% block name %}    定义可被替换的区块
# {% extends "..." %} 继承另一个模板
#
# 模板文件默认放在 templates/ 目录下
# ============================================
