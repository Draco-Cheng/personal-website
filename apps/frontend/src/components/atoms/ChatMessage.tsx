import React from "react";
import styles from "./ChatMessage.module.css";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ role, content }) => {
  return (
    <div className={`${styles.message} ${styles[role]}`}>
      <div className={styles.bubble}>{content}</div>
    </div>
  );
};

export default ChatMessage;
