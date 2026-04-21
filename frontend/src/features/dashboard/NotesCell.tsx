import { useState, useRef } from "react"
import { Input } from "@/components/ui/input"

interface NotesCellProps {
  value: string
  onSave: (value: string) => void
}

export function NotesCell({ value, onSave }: NotesCellProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(value)
  const inputRef = useRef<HTMLInputElement>(null)

  function startEdit() {
    setDraft(value)
    setEditing(true)
    setTimeout(() => inputRef.current?.focus(), 0)
  }

  function commit() {
    setEditing(false)
    if (draft !== value) onSave(draft)
  }

  if (editing) {
    return (
      <Input
        ref={inputRef}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={commit}
        onKeyDown={(e) => { if (e.key === "Enter") commit(); if (e.key === "Escape") setEditing(false) }}
        className="h-7 text-xs"
      />
    )
  }

  return (
    <span
      className="text-xs text-muted-foreground cursor-pointer hover:text-foreground transition-colors"
      onClick={startEdit}
    >
      {value || <span className="italic">Click to add notes</span>}
    </span>
  )
}
