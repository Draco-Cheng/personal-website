"use client";

import React, { useState } from "react";
import { MessageSquareText, X } from "lucide-react";

import ChatWindow from "../organisms/ChatWindow";
import { useChatbot } from "../../hooks/useChatbot";
import styles from "./ChatbotWidget.module.css";

const ChatbotWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { messages, loading, sendMessage } = useChatbot();

  const toggleChat = () => {
    setIsOpen((prev) => !prev);
  };

  return (
    <div className={styles.widget}>
      {isOpen && (
        <div className={styles.chatContainer}>
          <ChatWindow
            messages={messages}
            onSendMessage={sendMessage}
            loading={loading}
            onClose={toggleChat}
          />
        </div>
      )}

      <button
        className={styles.bubble}
        onClick={toggleChat}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? <X /> : <MessageSquareText />}
      </button>
    </div>
  );
};

export default ChatbotWidget;
