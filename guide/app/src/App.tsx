import { useState, useEffect } from "react";
import { Sun, Moon, GraduationCap } from "lucide-react";
import Sidebar from "./components/Sidebar";
import ContentView from "./components/ContentView";
import { chapters, type Chapter } from "./data/chapters";

function App() {
  const [activeChapter, setActiveChapter] = useState<Chapter>(chapters[0]);
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", isDark);
  }, [isDark]);

  return (
    <div className={`flex min-h-screen ${isDark ? "bg-slate-950 text-white" : "bg-white text-slate-900"}`}>
      {/* Sidebar */}
      <Sidebar activeChapterId={activeChapter.id} onSelectChapter={setActiveChapter} />

      {/* Main content area */}
      <div className="ml-72 flex flex-1 flex-col">
        {/* Top bar */}
        <header
          className={`sticky top-0 z-10 flex items-center justify-between border-b px-8 py-3 backdrop-blur ${
            isDark
              ? "border-slate-800 bg-slate-950/80"
              : "border-slate-200 bg-white/80"
          }`}
        >
          <div className="flex items-center gap-3">
            <GraduationCap size={24} className={isDark ? "text-indigo-400" : "text-indigo-600"} />
            <h1 className={`text-lg font-semibold ${isDark ? "text-white" : "text-slate-900"}`}>
              AI Learning Portal
            </h1>
          </div>
          <button
            onClick={() => setIsDark((prev) => !prev)}
            className={`rounded-lg p-2 transition-colors ${
              isDark
                ? "text-slate-400 hover:bg-slate-800 hover:text-white"
                : "text-slate-500 hover:bg-slate-100 hover:text-slate-900"
            }`}
            aria-label="Toggle dark mode"
          >
            {isDark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </header>

        {/* Content */}
        <main className="flex-1">
          <ContentView chapter={activeChapter} isDark={isDark} />
        </main>
      </div>
    </div>
  );
}

export default App;
