import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { debounce } from "@/lib/utils";
import { useEffect, useMemo } from "react";

interface TicketSearchProps {
  value: string;
  onChange: (value: string) => void;
  debounceMs?: number;
}

export function TicketSearch({
  value,
  onChange,
  debounceMs = 300,
}: TicketSearchProps) {
  const debouncedOnChange = useMemo(
    () => debounce((val: string) => onChange(val), debounceMs),
    [onChange, debounceMs],
  );

  useEffect(() => {
    return () => {
      // Cleanup debounce on unmount
    };
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    debouncedOnChange(newValue);
  };

  return (
    <div className="relative">
      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        type="text"
        placeholder="搜索 Ticket..."
        className="pl-9"
        defaultValue={value}
        onChange={handleChange}
      />
    </div>
  );
}
