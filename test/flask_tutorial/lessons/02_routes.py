# ============================================
# 第2课：路由——不同的URL返回不同的内容
# 运行：python lessons/02_routes.py
# 依次访问：
#   http://127.0.0.1:5000
#   http://127.0.0.1:5000/about
#   http://127.0.0.1:5000/user/tom
#   http://127.0.0.1:5000/post/2024/hello-world
# ============================================

from flask import Flask

app = Flask(__name__)


# ----- 普通路由：固定的URL -----

@app.route("/")
def home():
    return "<h1>🏠 首页</h1><p>欢迎来到我的网站！</p>"


@app.route("/about")
def about():
    return "<h1>📖 关于</h1><p>这个网站是用 Flask 搭建的。</p>"


# ----- 动态路由：URL 中包含变量 -----

# <username> 是占位符，可以匹配任意字符串
# 访问 /user/tom 时，username 的值就是 "tom"
@app.route("/user/<username>")
def user_profile(username):
    return f"<h1>👤 用户：{username}</h1><p>这是 {username} 的个人主页</p>"


# 可以有多个动态部分
# 访问 /post/2024/hello-world 时，year="2024", slug="hello-world"
@app.route("/post/<int:year>/<slug>")
def show_post(year, slug):
    return f"<h1>📝 文章</h1><p>年份：{year}<br>标题：{slug}</p>"


# ----- 指定变量类型 -----
# <int:id>  只匹配整数
# <float:n> 只匹配小数
# <path:p>  匹配包含斜杠的路径
# 不写类型默认为 string

@app.route("/item/<int:item_id>")
def item_detail(item_id):
    return f"<h1>📦 商品 #{item_id}</h1><p>这是第 {item_id} 号商品的详情页</p>"


if __name__ == "__main__":
    app.run(debug=True)


# ============================================
# 核心知识点：
#
# 1. @app.route("/路径")  - 把一个函数绑定到一个URL
#    函数叫什么名字不重要，但最好见名知意
#
# 2. <变量名>             - 动态路由，URL中的这部分会被捕获
#    函数参数名必须和URL中的变量名一致！
#
# 3. <类型:变量名>        - 指定变量类型做自动校验
#    string（默认）: 任意文本（不含斜杠）
#    int            : 只匹配整数，自动转为 int 类型
#    float          : 只匹配小数，自动转为 float 类型
#    path           : 匹配包含斜杠的路径
#
# 4. 返回 HTML 标签       - 直接在字符串里写HTML就能显示
#    （下一课会讲更好的方式——模板）
# ============================================
