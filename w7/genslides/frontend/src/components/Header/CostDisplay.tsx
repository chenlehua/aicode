/**
 * Cost display component
 */

import type { CostInfo } from "@/types";
import { formatCost } from "@/utils";

interface CostDisplayProps {
  cost: CostInfo | null;
}

export function CostDisplay({ cost }: CostDisplayProps): JSX.Element {
  if (!cost) {
    return <span className="text-sm text-[var(--md-slate)]">--</span>;
  }

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-[var(--md-slate)]">
        {cost.total_images} images
      </span>
      <span className="font-bold text-[var(--md-ink)]">
        {formatCost(cost.estimated_cost)}
      </span>
    </div>
  );
}
