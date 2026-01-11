import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'
import { debounce } from '@/lib/utils'
import { useEffect, useMemo } from 'react'

interface TicketSearchProps {
  value: string
  onChange: (value: string) => void
  debounceMs?: number
}

export function TicketSearch({ value, onChange, debounceMs = 300 }: TicketSearchProps) {
  const debouncedOnChange = useMemo(
    () => debounce((val: string) => onChange(val), debounceMs),
    [onChange, debounceMs]
  )

  useEffect(() => {
    return () => {
      // Cleanup debounce on unmount
    }
  }, [])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    debouncedOnChange(newValue)
  }

  return (
    <div className="relative group">
      <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground transition-colors duration-200 group-focus-within:text-foreground" />
      <Input
        type="text"
        placeholder="搜索 Ticket..."
        className="pl-11 pr-4 bg-muted/30 border-muted/50 focus-visible:bg-background focus-visible:border-ring/50 transition-all duration-200"
        defaultValue={value}
        onChange={handleChange}
      />
    </div>
  )
}
