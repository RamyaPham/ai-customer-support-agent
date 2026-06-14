import { chapters, type Chapter } from "../data/chapters";
import { BookOpen, Cpu } from "lucide-react";

interface SidebarProps {
  activeChapterId: string;
  onSelectChapter: (chapter: Chapter) => void;
}

const groupConfig = {
  concepts: {
    label: "Core Concepts",
    icon: BookOpen,
  },
  tech: {
    label: "Technology Deep-Dives",
    icon: Cpu,
  },
} as const;

export default function Sidebar({ activeChapterId, onSelectChapter }: SidebarProps) {
  const conceptChapters = chapters.filter((c) => c.group === "concepts");
  const techChapters = chapters.filter((c) => c.group === "tech");

  const renderGroup = (group: "concepts" | "tech", items: Chapter[]) => {
    const config = groupConfig[group];
    const Icon = config.icon;

    return (
      <div className="mb-6">
        <div className="flex items-center gap-2 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <Icon size={14} />
          <span>{config.label}</span>
        </div>
        <ul className="space-y-0.5">
          {items.map((chapter) => {
            const isActive = chapter.id === activeChapterId;
            return (
              <li key={chapter.id}>
                <button
                  onClick={() => onSelectChapter(chapter)}
                  className={`flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm transition-colors ${
                    isActive
                      ? "border-r-2 border-indigo-400 bg-slate-800 text-white"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
                  }`}
                >
                  <span
                    className={`flex h-6 w-6 shrink-0 items-center justify-center rounded text-xs font-medium ${
                      isActive
                        ? "bg-indigo-500 text-white"
                        : "bg-slate-700 text-slate-400"
                    }`}
                  >
                    {chapter.number}
                  </span>
                  <span className="truncate">{chapter.title}</span>
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    );
  };

  return (
    <aside className="fixed left-0 top-0 z-20 flex h-screen w-72 flex-col bg-slate-900">
      <div className="flex items-center gap-2 border-b border-slate-700 px-5 py-4">
        <BookOpen size={20} className="text-indigo-400" />
        <span className="text-sm font-semibold text-white">Chapters</span>
      </div>
      <nav className="flex-1 overflow-y-auto py-4">
        {renderGroup("concepts", conceptChapters)}
        {renderGroup("tech", techChapters)}
      </nav>
    </aside>
  );
}
