import { useState } from "react";
import { MessageSquare, LayoutDashboard, Headphones } from "lucide-react";
import ChatWindow from "./components/ChatWindow";
import AdminDashboard from "./components/AdminDashboard";

type Tab = "chat" | "admin";

function App() {
  const [tab, setTab] = useState<Tab>("chat");

  return (
    <div className="h-screen flex flex-col bg-slate-50">
      <header className="bg-gradient-to-r from-indigo-600 to-indigo-800 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-white/20 p-2 rounded-lg">
              <Headphones size={22} />
            </div>
            <div>
              <h1 className="text-lg font-bold tracking-tight">AI Refund Agent</h1>
              <p className="text-indigo-200 text-xs">E-commerce Customer Support</p>
            </div>
          </div>
          <nav className="flex gap-1 bg-indigo-900/30 rounded-lg p-1">
            <button
              onClick={() => setTab("chat")}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                tab === "chat"
                  ? "bg-white text-indigo-700 shadow-sm"
                  : "text-indigo-200 hover:text-white hover:bg-white/10"
              }`}
            >
              <MessageSquare size={16} />
              Chat
            </button>
            <button
              onClick={() => setTab("admin")}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                tab === "admin"
                  ? "bg-white text-indigo-700 shadow-sm"
                  : "text-indigo-200 hover:text-white hover:bg-white/10"
              }`}
            >
              <LayoutDashboard size={16} />
              Admin
            </button>
          </nav>
        </div>
      </header>

      <main className="flex-1 overflow-hidden">
        <div className="max-w-7xl mx-auto h-full">
          {tab === "chat" ? <ChatWindow /> : <AdminDashboard />}
        </div>
      </main>
    </div>
  );
}

export default App;
