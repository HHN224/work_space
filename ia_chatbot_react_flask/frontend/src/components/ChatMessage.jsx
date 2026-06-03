export default function ChatMessage ({ question, answer}){
    return(
        <div className="message">
            <div className="user-message">{question}</div>
            <div className="chatbot-message">{answer}</div>
        </div>
    );
}