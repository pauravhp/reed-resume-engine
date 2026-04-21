import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import type { ExperienceOutput } from "@/hooks/useGenerate"

interface ExperienceEditorProps {
  experiences: ExperienceOutput[]
  /** Set of bullet strings that are checked (included) */
  checkedBullets: Set<string>
  onToggleBullet: (bullet: string, checked: boolean) => void
}

export function ExperienceEditor({
  experiences,
  checkedBullets,
  onToggleBullet,
}: ExperienceEditorProps) {
  return (
    <div className="space-y-4">
      {experiences.map((exp) => (
        <div key={`${exp.company}-${exp.role_title}`}>
          <p className="text-sm font-medium mb-1">
            {exp.company}
            <span className="text-muted-foreground font-normal"> · {exp.role_title}</span>
          </p>
          <div className="space-y-1.5 pl-1">
            {exp.bullets.map((bullet, i) => {
              const id = `${exp.company}-${i}`
              return (
                <div key={id} className="flex items-start gap-2">
                  <Checkbox
                    id={id}
                    checked={checkedBullets.has(bullet)}
                    onCheckedChange={(checked) => onToggleBullet(bullet, !!checked)}
                    className="mt-0.5 shrink-0"
                  />
                  <Label htmlFor={id} className="text-sm leading-snug font-normal cursor-pointer">
                    {bullet}
                  </Label>
                </div>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
