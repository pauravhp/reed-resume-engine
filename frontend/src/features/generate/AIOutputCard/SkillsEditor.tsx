import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { SkillsOutput } from "@/hooks/useGenerate"

interface SkillsEditorProps {
  value: SkillsOutput
  onChange: (value: SkillsOutput) => void
}

export function SkillsEditor({ value, onChange }: SkillsEditorProps) {
  return (
    <div className="space-y-2.5">
      {(["languages", "frameworks", "tools"] as const).map((field) => (
        <div key={field} className="grid grid-cols-[100px_1fr] items-center gap-3">
          <Label className="text-xs text-muted-foreground capitalize">{field}</Label>
          <Input
            value={value[field]}
            onChange={(e) => onChange({ ...value, [field]: e.target.value })}
            className="h-8 text-sm"
          />
        </div>
      ))}
    </div>
  )
}
