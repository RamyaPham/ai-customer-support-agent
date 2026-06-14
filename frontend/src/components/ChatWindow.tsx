import { useState, useRef, useEffect } from "react";
import { Send, Loader2, MessageCircle, RotateCcw } from "lucide-react";
import { sendMessage, type ChatResponse, type TraceStep } from "../api";
import DecisionBadge from "./DecisionBadge";

interface Message {
  role: "user" | "assistant";
  content: string;
  decision?: string | null;
}

interface Props {
  onTrace?: (trace: TraceStep[], runId: string) => void;
}

export default function ChatWindow({ onTrace }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [runId, setRunId] = useState<string | undefined>();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const res: ChatResponse = await sendMessage(text, runId);
      setRunId(res.run_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.reply, decision: res.decision },
      ]);
      if (onTrace && res.trace.length > 0) {
        onTrace(res.trace, res.run_id);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: Could not reach the server. Please check the backend is running." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleNew = () => {
    setMessages([]);
    setRunId(undefined);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-6 py-3 border-b border-slate-200 bg-white">
        <div className="flex items-center gap-2">
          <MessageCircle size={18} className="text-indigo-500" />
          <h2 className="text-base font-semibold text-slate-800">Customer Support</h2>
        </div>
        <button
          onClick={handleNew}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-indigo-600 transition-colors"
        >
          <RotateCcw size={14} />
          New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50">
        {messages.length === 0 && (
          <div className="text-center mt-24">
            <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <MessageCircle size={28} className="text-indigo-500" />
            </div>
            <p className="text-lg font-medium text-slate-700">Welcome! How can I help you?</p>
            <p className="text-sm text-slate-400 mt-1">Ask about a refund for any of your orders.</p>
            <div className="mt-6 flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
              {[
                "I'd like a refund for my order",
                "What's your refund policy?",
                "Can I return a final-sale item?",
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setInput(suggestion)}
                  className="text-xs px-3 py-1.5 rounded-full bg-white border border-slate-200 text-slate-600 hover:border-indigo-300 hover:text-indigo-600 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-3 shadow-sm ${
                m.role === "user"
                  ? "bg-indigo-600 text-white"
                  : "bg-white border border-slate-200 text-slate-800"
              }`}
            >
              <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.content}</p>
              {m.decision && (
                <div className="mt-2">
                  <DecisionBadge decision={m.decision} />
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-slate-200 rounded-2xl px-4 py-3 shadow-sm">
              <div className="flex items-center gap-2 text-slate-400">
                <Loader2 size={16} className="animate-spin" />
                <span className="text-xs">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-slate-200 bg-white p-4">
        <div className="flex gap-2 max-w-3xl mx-auto">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Type your message..."
            className="flex-1 border border-slate-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder-slate-400"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="bg-indigo-600 text-white rounded-xl px-5 py-2.5 hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
