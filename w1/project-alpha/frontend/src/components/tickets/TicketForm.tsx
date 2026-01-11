import { useState, useEffect } from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { TagSelector } from '@/components/tags/TagSelector'
import { CreateTicketInput, UpdateTicketInput, Tag } from '@/types'

interface TicketFormProps {
  tags: Tag[]
  initialData?: CreateTicketInput | UpdateTicketInput
  onSubmit: (data: CreateTicketInput | UpdateTicketInput) => void
  onCancel?: () => void
  onNewTag?: () => void
  isLoading?: boolean
}

export function TicketForm({
  tags,
  initialData,
  onSubmit,
  onCancel,
  onNewTag,
  isLoading = false,
}: TicketFormProps) {
  const [title, setTitle] = useState(initialData?.title || '')
  const [description, setDescription] = useState(initialData?.description || '')
  const [tagIds, setTagIds] = useState<string[]>(initialData?.tagIds || [])

  useEffect(() => {
    if (initialData) {
      setTitle(initialData.title)
      setDescription(initialData.description || '')
      setTagIds(initialData.tagIds || [])
    }
  }, [initialData])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return
    onSubmit({
      title: title.trim(),
      description: description.trim() || undefined,
      tagIds,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-3">
        <Label htmlFor="ticket-title" className="text-base">
          标题 *
        </Label>
        <Input
          id="ticket-title"
          value={title}
          onChange={e => setTitle(e.target.value)}
          placeholder="输入 Ticket 标题"
          required
          maxLength={255}
        />
      </div>
      <div className="space-y-3">
        <Label htmlFor="ticket-description" className="text-base">
          描述
        </Label>
        <Textarea
          id="ticket-description"
          value={description}
          onChange={e => setDescription(e.target.value)}
          placeholder="输入 Ticket 描述（可选）"
          rows={5}
        />
      </div>
      <TagSelector
        tags={tags}
        selectedTagIds={tagIds}
        onChange={setTagIds}
        onNewTag={onNewTag}
        allowCreate={!!onNewTag}
      />
      <div className="flex gap-3 justify-end pt-4">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            取消
          </Button>
        )}
        <Button type="submit" disabled={isLoading || !title.trim()}>
          {isLoading ? '保存中...' : '保存'}
        </Button>
      </div>
    </form>
  )
}
