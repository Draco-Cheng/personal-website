import React, { useEffect, useRef } from "react";
import ChatMessage from "../atoms/ChatMessage";
import ChatInput from "../molecules/ChatInput";
import type { ChatMessage as ChatMessageType } from "../../hooks/useChatbot";
import styles from "./ChatWindow.module.css";

interface ChatWindowProps {
  messages: ChatMessageType[];
  onSendMessage: (message: string) => void;
  loading: boolean;
  onClose: () => void;
}

const WELCOME_MESSAGE: ChatMessageType = {
  role: "assistant",
  content: "Hi! I'm here to help you learn about Draco's experience and projects. Feel free to ask me anything!",
};

const ChatWindow: React.FC<ChatWindowProps> = ({
  messages,
  onSendMessage,
  loading,
  onClose,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const displayMessages = messages.length === 0 ? [WELCOME_MESSAGE] : messages;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className={styles.window}>
      <div className={styles.header}>
        <h3 className={styles.title}>Chat with Draco's AI Assistant</h3>
        <button
          onClick={onClose}
          className={styles.closeButton}
          aria-label="Close chat"
        >
          ✕
        </button>
      </div>

      <div className={styles.messages}>
        {displayMessages.map((message, index) => (
          <ChatMessage
            key={index}
            role={message.role}
            content={message.content}
          />
        ))}
        {loading && (
          <div className={styles.typingIndicator}>
            <span></span>
            <span></span>
            <span></span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <ChatInput onSend={onSendMessage} disabled={loading} />
    </div>
  );
};

export default ChatWindow;
