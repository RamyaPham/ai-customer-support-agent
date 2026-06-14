# Chapter 13: React, Tailwind CSS, and Vite -- The Frontend Stack

## Why We Chose This

React is the industry-standard library for building interactive UIs. Tailwind CSS provides utility classes that let you style components without writing separate CSS files. Vite is a build tool that starts a development server in milliseconds and hot-reloads changes instantly. Together, they let us build a polished chat interface and admin dashboard with minimal boilerplate.

## How It Works In Our Project

### Vite Configuration and the API Proxy

```typescript
// frontend/vite.config.ts
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: { "/api": "http://localhost:8000" },
  },
});
```

The proxy line is critical. During development, the React app runs on port 5173 and the FastAPI backend on port 8000. The proxy tells Vite: "any request to `/api/*` should be forwarded to the backend." This means our frontend code can call `/api/chat` without knowing the backend's port -- and avoids CORS issues in development.

### The API Layer

```typescript
// frontend/src/api.ts
const API_BASE = "/api";

export async function sendMessage(message: string, runId?: string): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, run_id: runId }),
  });
  if (!res.ok) throw new Error(`Chat failed: ${res.status}`);
  return res.json();
}
```

All backend communication goes through `api.ts`. TypeScript interfaces (`ChatResponse`, `TraceStep`, `RunSummary`) mirror the backend Pydantic models, so type mismatches are caught at compile time.

### Component Architecture

**App.tsx** -- The root component. Manages tab navigation between Chat and Admin views:

```tsx
function App() {
  const [tab, setTab] = useState<Tab>("chat");
  return (
    <div className="h-screen flex flex-col bg-slate-50">
      <header className="bg-gradient-to-r from-indigo-600 to-indigo-800 ...">
        {/* Navigation tabs */}
      </header>
      <main className="flex-1 overflow-hidden">
        {tab === "chat" ? <ChatWindow /> : <AdminDashboard />}
      </main>
    </div>
  );
}
```

**ChatWindow** -- The customer-facing chat. Manages message state, sends user input to the API, renders the conversation with bubble styling, and displays a `DecisionBadge` when the agent reaches a verdict.

**AdminDashboard** -- The operator view. Fetches all conversation runs from `/api/runs`, displays them in a sidebar, and renders a detailed trace timeline when a run is selected. Each trace step shows the tool name, inputs, outputs, latency, and token counts via `TraceStepCard`.

### Tailwind in Practice

Notice how styles are applied directly in the JSX:

```tsx
<div className="bg-indigo-600 text-white rounded-xl px-5 py-2.5 hover:bg-indigo-700 
                disabled:opacity-40 transition-colors shadow-sm">
```

Each class is a single CSS property. `bg-indigo-600` sets the background color, `rounded-xl` adds border radius, `hover:bg-indigo-700` changes color on hover. No separate stylesheet needed.

## Key Takeaways

- **Vite's proxy** bridges frontend and backend during development, letting the UI call `/api/*` without hardcoding ports.
- **TypeScript interfaces** in `api.ts` mirror backend Pydantic models for end-to-end type safety.
- **Component architecture** separates concerns: `App` handles routing, `ChatWindow` handles the customer experience, `AdminDashboard` handles observability.
- **Tailwind utility classes** keep styles co-located with markup, making components self-contained and easy to modify.
