"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

export interface Message {
  role: "user" | "assistant" | "tool";
  content: string;
  toolName?: string;
}

interface ChatContextType {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
}

const ChatContext = createContext<ChatContextType>({ messages: [], setMessages: () => {} });

const STORAGE_KEY = "offerpilot-chat-history";

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<Message[]>(() => {
    if (typeof window === "undefined") return [];
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch { return []; }
  });

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(messages)); } catch {}
  }, [messages]);

  return <ChatContext.Provider value={{ messages, setMessages }}>{children}</ChatContext.Provider>;
}

export function useChatMessages() {
  return useContext(ChatContext);
}
