import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import type { Chapter } from "../data/chapters";

interface ContentViewProps {
  chapter: Chapter;
  isDark: boolean;
}

export default function ContentView({ chapter, isDark }: ContentViewProps) {
  const emptyState = (
    <div className={`flex flex-col items-center justify-center py-32 ${isDark ? "text-slate-500" : "text-slate-400"}`}>
      <p className="text-lg">Content coming soon.</p>
      <p className="mt-1 text-sm">This chapter is a placeholder and will be filled by another agent.</p>
    </div>
  );

  return (
    <article className="mx-auto max-w-3xl px-8 py-10">
      <div className="mb-8">
        <span className={`text-sm font-medium ${isDark ? "text-indigo-400" : "text-indigo-600"}`}>
          Chapter {chapter.number}
        </span>
        <h1 className={`mt-1 text-3xl font-bold ${isDark ? "text-white" : "text-slate-900"}`}>
          {chapter.title}
        </h1>
      </div>

      {chapter.content ? (
        <div className={`prose max-w-none ${isDark ? "prose-invert" : ""}`}>
          <ReactMarkdown
            components={{
              h1: ({ children }) => (
                <h1 className={`mb-4 mt-10 text-2xl font-bold ${isDark ? "text-white" : "text-slate-900"}`}>
                  {children}
                </h1>
              ),
              h2: ({ children }) => (
                <h2 className={`mb-3 mt-8 text-xl font-semibold ${isDark ? "text-white" : "text-slate-800"}`}>
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className={`mb-2 mt-6 text-lg font-semibold ${isDark ? "text-slate-200" : "text-slate-700"}`}>
                  {children}
                </h3>
              ),
              p: ({ children }) => (
                <p className={`my-3 leading-7 ${isDark ? "text-slate-300" : "text-slate-600"}`}>
                  {children}
                </p>
              ),
              ul: ({ children }) => (
                <ul className={`my-4 list-disc space-y-1 pl-6 ${isDark ? "text-slate-300" : "text-slate-600"}`}>
                  {children}
                </ul>
              ),
              ol: ({ children }) => (
                <ol className={`my-4 list-decimal space-y-1 pl-6 ${isDark ? "text-slate-300" : "text-slate-600"}`}>
                  {children}
                </ol>
              ),
              li: ({ children }) => (
                <li className="leading-7">{children}</li>
              ),
              blockquote: ({ children }) => {
                // Detect "Key Takeaways" sections
                const text = String(children);
                const isKeyTakeaway = text.toLowerCase().includes("key takeaway");
                if (isKeyTakeaway) {
                  return (
                    <div className={`my-6 rounded-lg border-l-4 p-5 ${
                      isDark
                        ? "border-indigo-400 bg-indigo-950/40 text-slate-200"
                        : "border-indigo-500 bg-indigo-50 text-slate-700"
                    }`}>
                      {children}
                    </div>
                  );
                }
                return (
                  <blockquote className={`my-4 border-l-4 pl-4 italic ${
                    isDark
                      ? "border-slate-600 text-slate-400"
                      : "border-slate-300 text-slate-500"
                  }`}>
                    {children}
                  </blockquote>
                );
              },
              code: ({ className, children, ...props }) => {
                const match = /language-(\w+)/.exec(className || "");
                const inline = !match;
                if (inline) {
                  return (
                    <code
                      className={`rounded px-1.5 py-0.5 text-sm font-mono ${
                        isDark
                          ? "bg-slate-700 text-indigo-300"
                          : "bg-slate-100 text-indigo-600"
                      }`}
                      {...props}
                    >
                      {children}
                    </code>
                  );
                }
                return (
                  <SyntaxHighlighter
                    style={oneDark}
                    language={match[1]}
                    PreTag="div"
                    className="my-4 rounded-lg !text-sm"
                  >
                    {String(children).replace(/\n$/, "")}
                  </SyntaxHighlighter>
                );
              },
              a: ({ href, children }) => (
                <a
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`underline ${isDark ? "text-indigo-400 hover:text-indigo-300" : "text-indigo-600 hover:text-indigo-500"}`}
                >
                  {children}
                </a>
              ),
              strong: ({ children }) => (
                <strong className={`font-semibold ${isDark ? "text-white" : "text-slate-900"}`}>
                  {children}
                </strong>
              ),
            }}
          >
            {chapter.content}
          </ReactMarkdown>
        </div>
      ) : (
        emptyState
      )}
    </article>
  );
}
