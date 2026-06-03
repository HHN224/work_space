import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import TextLoader

load_dotenv()
api_key = os.getenv('DEEPSEEK_API_KEY')
model = "deepseek-chat"
deepseek = ChatOpenAI(
    api_key=api_key,
    model=model,
    base_url="https://api.deepseek.com"
)

parser = StrOutputParser()
deepseek_chain = deepseek | parser

loader = TextLoader('data.txt', encoding='utf-8')
data = loader.load()

template = ("""
你是一个智能聊天机器人，专门根据下面提供的上下文信息来回答问题。
只回答被问到的问题，不要主动提供多余的信息。
回答尽量简短精炼，不要长篇大论。
介绍自己时，说你是一个基于个人信息打造的 AI 助手，目标是帮助别人了解上下文中的那个人。
绝对不要编造任何信息。
如果被问到上下文中没有涉及的内容，请一律如实回答："抱歉，我没有关于这方面的信息，如果想了解更多可以当面交流！"
你要假设自己就是上下文中描述的那个人，用第一人称进行回答。
上下文:{context}
问题:{question}
            
"""
            )

def get_chatbot_response(user_question):
    final_template = template.format(context = data, question = user_question)
    answer = deepseek_chain.invoke(final_template)
    return answer

if __name__ == '__main__':
    question = '你是谁'
    final_template = template.format(context = data, question = question)
    answer = deepseek_chain.invoke(final_template)
    print(answer)