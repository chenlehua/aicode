import { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { CreateTagInput, UpdateTagInput } from '@/types'
import { cn } from '@/lib/utils'

const PRESET_COLORS = [
  '#ef4444', // Red
  '#f97316', // Orange
  '#f59e0b', // Amber
  '#22c55e', // Green
  '#14b8a6', // Teal
  '#3b82f6', // Blue
  '#6366f1', // Indigo
  '#8b5cf6', // Violet
  '#ec4899', // Pink
  '#6b7280', // Gray
]

interface TagFormProps {
  initialData?: CreateTagInput | UpdateTagInput
  onSubmit: (data: CreateTagInput | UpdateTagInput) => void
  onCancel?: () => void
  isLoading?: boolean
}

export function TagForm({ initialData, onSubmit, onCancel, isLoading = false }: TagFormProps) {
  const [name, setName] = useState(initialData?.name || '')
  const [color, setColor] = useState(initialData?.color || PRESET_COLORS[0])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    onSubmit({ name: name.trim(), color })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-3">
        <Label htmlFor="tag-name" className="text-base">
          标签名称
        </Label>
        <Input
          id="tag-name"
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="输入标签名称"
          required
          maxLength={50}
        />
      </div>
      <div className="space-y-4">
        <Label className="text-base">标签颜色</Label>
        <div className="flex flex-wrap gap-3">
          {PRESET_COLORS.map(presetColor => (
            <button
              key={presetColor}
              type="button"
              className={cn(
                'w-10 h-10 rounded-xl border-2 transition-all duration-200 shadow-sm hover:shadow-md hover:scale-110 active:scale-95',
                color === presetColor
                  ? 'border-foreground scale-110 ring-2 ring-primary/20'
                  : 'border-transparent hover:border-foreground/20'
              )}
              style={{ backgroundColor: presetColor }}
              onClick={() => setColor(presetColor)}
            />
          ))}
        </div>
        <div className="flex items-center gap-3">
          <Input
            type="color"
            value={color}
            onChange={e => setColor(e.target.value)}
            className="w-16 h-12 rounded-xl cursor-pointer"
          />
          <Input
            type="text"
            value={color}
            onChange={e => setColor(e.target.value)}
            placeholder="#6366f1"
            pattern="^#[0-9A-Fa-f]{6}$"
            className="flex-1"
          />
        </div>
      </div>
      <div className="flex gap-3 justify-end pt-4">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            取消
          </Button>
        )}
        <Button type="submit" disabled={isLoading || !name.trim()}>
          {isLoading ? '保存中...' : '保存'}
        </Button>
      </div>
    </form>
  )
}
