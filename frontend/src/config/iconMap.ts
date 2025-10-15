import type { LucideIcon } from "lucide-react";
import { Zap, Clock, DollarSign, Check, Sparkles, Brain } from "lucide-react";

export const iconMap: Record<string, LucideIcon> = {
  Zap,
  Clock,
  DollarSign,
  Check,
  Sparkles,
  Brain,
};

export function getIcon(name?: string): LucideIcon {
  if (!name) return Check;
  return iconMap[name] ?? Check;
}