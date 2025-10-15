import type { LucideIcon } from "lucide-react";
import { Zap, Clock, DollarSign, Check } from "lucide-react";

export const iconMap: Record<string, LucideIcon> = {
  Zap,
  Clock,
  DollarSign,
  Check,
};

export function getIcon(name?: string): LucideIcon {
  if (!name) return Check;
  return iconMap[name] ?? Check;
}