"use client";

import ReactMarkdown from "react-markdown";
import { Message } from "@/lib/chat-context";

export function ChatMessage({ msg }: { msg: Message }) {
  if (msg.role === "user") {
    return (
      <div className="flex justify-end mb-4">
        <div className="bg-zinc-900 text-white rounded-2xl rounded-br-md px-4 py-2.5 max-w-[70%] text-sm">
          {msg.content}
        </div>
      </div>
    );
  }
  if (msg.role === "tool") {
    return (
      <div className="mb-2 ml-2">
        <details className="text-xs">
          <summary className="cursor-pointer text-zinc-400 font-mono hover:text-zinc-600">
            🔧 {msg.toolName || "tool"}
          </summary>
          <pre className="mt-1 p-2 bg-zinc-50 rounded text-zinc-600 overflow-x-auto max-h-32 text-[11px]">
            {msg.content.slice(0, 1000)}
          </pre>
        </details>
      </div>
    );
  }
  return (
    <div className="flex justify-start mb-4">
      <div className="bg-zinc-100 rounded-2xl rounded-bl-md px-4 py-2.5 max-w-[75%] text-sm prose prose-sm prose-zinc prose-table:text-xs overflow-y-auto max-h-[60vh]">
        <ReactMarkdown components={{ a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{children}</a> }}>{msg.content}</ReactMarkdown>
      </div>
    </div>
  );
}
