from flask import Flask, render_template, request, url_for, flash, redirect, url_for, jsonify
from flask_cors import CORS # type: ignore
from main import get_chatbot_response
import re

app = Flask(__name__)
CORS(app)
conversation = []

def clean_response(response):
    return response.split("</think>")[-1].strip()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_question = data.get('message', '')
    raw_response = get_chatbot_response(user_question)
    clean = clean_response(raw_response)
    return jsonify({'response':clean})

if __name__ == '__main__':
    app.run(debug=True)
