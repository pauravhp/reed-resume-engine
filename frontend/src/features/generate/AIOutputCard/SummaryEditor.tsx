import { Textarea } from "@/components/ui/textarea"

interface SummaryEditorProps {
  value: string
  onChange: (value: string) => void
}

export function SummaryEditor({ value, onChange }: SummaryEditorProps) {
  return (
    <Textarea
      value={value}
      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => onChange(e.target.value)}
      rows={4}
      className="resize-none text-sm"
      placeholder="AI-generated summary will appear here..."
    />
  )
}
