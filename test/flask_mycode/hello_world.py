from flask import Flask, render_template, request, redirect, url_for
import os
import json

app = Flask(__name__, template_folder="templates", static_folder="static")

DATA_PATH = os.path.join(os.path.dirname(__file__), "data.json")

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

def load_todos():
    if not os.path.exists(DATA_PATH):
        return []
    else:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

def save_todos(todos):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)



@app.route("/todos", methods=["GET", "POST"])
def todos():
    todos = load_todos()
    if request.method == "POST":
        title = request.form.get("title")
        if title:
            new_id = max([t["id"] for t in todos], default=0) + 1
            todos.append({"id": new_id, "title": title, "done": False})
            save_todos(todos)
        return redirect(url_for("todos"))

    return render_template("todo_list.html", todos=todos)

@app.route("/todos/delete/<todo_id>", methods=["POST"])
def delete_todo(todo_id):
    todos = load_todos()
    todos = [t for t in todos if t["id"]!=int(todo_id)]
    save_todos(todos)
    return redirect(url_for("todos"))

@app.route("/todos/toggle/<todo_id>", methods=["POST"])
def toggle_todo(todo_id):
    todos = load_todos()
    for t in todos:
        if t["id"] == int(todo_id):
            t["done"] = not t["done"]
    save_todos(todos)
    return redirect(url_for("todos"))


messages = []
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        username = request.form.get("username")
        message = request.form.get('message')
        messages.append({"username": username, "message": message})
        return redirect(url_for("chat"))
    return render_template("chat.html", messages=messages)



if __name__ == '__main__':
    app.run(debug=True)