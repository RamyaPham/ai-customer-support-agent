import { CheckCircle, XCircle, AlertTriangle, HelpCircle } from "lucide-react";

interface Props {
  decision: string | null;
}

const CONFIG: Record<string, { color: string; Icon: typeof CheckCircle }> = {
  APPROVED: { color: "bg-emerald-50 text-emerald-700 border-emerald-200", Icon: CheckCircle },
  DENIED: { color: "bg-red-50 text-red-700 border-red-200", Icon: XCircle },
  ESCALATED: { color: "bg-amber-50 text-amber-700 border-amber-200", Icon: AlertTriangle },
  NEEDS_INFO: { color: "bg-sky-50 text-sky-700 border-sky-200", Icon: HelpCircle },
};

export default function DecisionBadge({ decision }: Props) {
  if (!decision) return null;
  const { color, Icon } = CONFIG[decision] || { color: "bg-slate-50 text-slate-700 border-slate-200", Icon: HelpCircle };
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-full border ${color}`}>
      <Icon size={12} />
      {decision}
    </span>
  );
}
