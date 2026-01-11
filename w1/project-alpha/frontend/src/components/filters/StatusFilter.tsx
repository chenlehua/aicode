import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export type TicketStatus = "all" | "open" | "completed";

interface StatusFilterProps {
  value: TicketStatus;
  onChange: (status: TicketStatus) => void;
}

const statusOptions: { value: TicketStatus; label: string }[] = [
  { value: "all", label: "所有" },
  { value: "open", label: "进行中" },
  { value: "completed", label: "已完成" },
];

export function StatusFilter({ value, onChange }: StatusFilterProps) {
  return (
    <div className="space-y-2">
      <div className="text-sm font-medium">状态筛选</div>
      <div className="flex flex-col gap-2">
        {statusOptions.map((option) => (
          <Button
            key={option.value}
            variant={value === option.value ? "default" : "outline"}
            className={cn(
              "w-full justify-start",
              value === option.value && "bg-primary text-primary-foreground",
            )}
            onClick={() => onChange(option.value)}
          >
            {option.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
