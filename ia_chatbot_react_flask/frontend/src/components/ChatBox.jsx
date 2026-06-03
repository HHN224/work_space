import ChatMessage from './ChatMessage';
import axios from 'axios';
import { useState, useRef, useEffect } from 'react';
import LoadingDots from './LoadingDots';




export default function ChatBox() {
    const [messages, setMessages] = useState([]);
    const [content, setContent] = useState('');
    const messagesEndRef = useRef(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!content.trim()) return;
        

        const userMessage = content;
        setContent('');
        setMessages(prev => [...prev, { question: userMessage, answer: <LoadingDots /> }]);

        try{
            const response = await axios.post('http://localhost:5000/api/chat', {
                message: userMessage,
            });
            const botReply = response.data.response;

            setMessages(prev => {
                const updated = [...prev];
                updated[updated.length -1].answer = botReply;
                return updated;
            });
        } catch (error){
            const errMsg = error.response?.data?.error || error.message || '连接服务器失败';
            setMessages(prev => {
                const updated = [...prev];
                updated[updated.length -1].answer = `Error: ${errMsg}`;
                return updated;
            });
        }
    };
    return(
        <>
        <div className="chat-history">
            {messages.map((msg, index) => (
                <ChatMessage key={index} question={msg.question} answer={msg.answer} />
            ))}
            <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSubmit} className="container-text-area">
            <textarea
            placeholder="输入你的消息..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            />
            <button type="submit">
                <i className="fa-solid fa-paper-plane"></i>
            </button>
        </form>
        </>
    );   
}