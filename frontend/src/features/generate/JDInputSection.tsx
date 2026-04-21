import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Zap } from "lucide-react"

interface JDInputSectionProps {
  value: string
  onChange: (value: string) => void
  onGenerate: () => void
  isLoading: boolean
}

export function JDInputSection({ value, onChange, onGenerate, isLoading }: JDInputSectionProps) {
  return (
    <div className="flex flex-col gap-3 h-full">
      <div>
        <h2 className="font-semibold text-base mb-0.5">Job Description</h2>
        <p className="text-sm text-muted-foreground">Paste the full job posting</p>
      </div>
      <Textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste job description here..."
        className="flex-1 min-h-[320px] resize-none text-sm"
      />
      <Button
        onClick={onGenerate}
        disabled={!value.trim() || isLoading}
        className="w-full gap-2"
      >
        <Zap className="h-4 w-4" />
        {isLoading ? "Generating…" : "Generate Resume"}
      </Button>
    </div>
  )
}
