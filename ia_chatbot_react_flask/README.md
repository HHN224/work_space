# 🤖 AI Chatbot with React & Flask

![Python](https://img.shields.io/badge/language-Python-pink)  ![Flask](https://img.shields.io/badge/framework-Flask-purple?logo=flask&logoColor=white) 
![JavaScript](https://img.shields.io/badge/language-JavaScript-pink)  ![React](https://img.shields.io/badge/framework-React-purple?logo=react&logoColor=white)

This project is an AI chatbot built with **React (frontend)** and **Flask (backend)**.  
It uses **LangChain** and **Groq** to process questions based on the content of a `.txt` file.

## 🧠 Features

- Ask questions to an AI powered by LangChain and Groq.
- Chat history is displayed with React.
- Text-based knowledge from a `.txt` file.
- Loading animation while the bot processes.

---

## ❗ Important

I wrote a .txt file where I included the information from my CV and my work experience, with the intention of creating a sort of virtual "me" so that recruiters viewing my resume could interact with it and ask any questions they might have about me.

But you can write a .txt file with anything you want, for example, it could contain frequently asked questions about a business.
( I didn’t upload my personalized .txt file to GitHub you’ll need to create your own )

- For this, I use the DeepSeek model: **deepseek-r1-distill-llama-70b**
- You’ll need an API key, which you can get for free at:
👉 https://console.groq.com/keys

Also, in the main.py file, you’ll see a variable called template. This is the "prompt" or set of instructions we give the model to tell it how it should behave. I wrote a custom one based on the specific purpose I had in mind. You can delete it and write your own prompt that fits your needs.


---

# How to launch:

## 🐍 Backend Setup (Flask)

2. Create a Virtual Environment

```
python -m venv venv
```
3. Activate the Environment

```
venv\Scripts\activate
```

4. Install Python Dependencies

```
pip install -r requirements.txt
```

5. Create a .env File

```
key = your credentials
```
you can get your own free API key in: https://console.groq.com/keys

6. Run the Flask Backend
```
flask run
```

## ⚛️ Frontend Setup (React)

7. Go to the Frontend Folder

```
cd frontend
```

8. Install Node Dependencies

```
npm install
```

9. Run the React Frontend

```
npm run dev
```

## ✅ Access the App

Once both servers are running go to the frontend one:

- Backend API: http://localhost:5000
- Frontend: http://localhost:5173 (or shown by Vite)

## 🔢 Versions

```
Python == 3.12.2
Flask==3.1.0
flask-cors==6.0.0
python-dotenv==1.0.1
langchain==0.3.20
langchain-community==0.3.19
langchain-core==0.3.41
langchain-groq==0.2.4
groq==0.18.0
```

Here are the versions I’m using, just in case you need compatibility with your Python environment


## Authors

**Maruxa Muncharaz** – [MaruSheik on GitHub](https://github.com/marusheik)  


## License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/marusheik/ia_chatbot_react_flask/blob/main/LICENSE) file for details

