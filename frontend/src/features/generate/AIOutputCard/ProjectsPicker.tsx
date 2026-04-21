import { cn } from "@/lib/utils"
import type { ProjectOutput } from "@/hooks/useGenerate"

interface ProjectsPickerProps {
  projects: ProjectOutput[]
  selectedIds: Set<string>
  onToggle: (id: string) => void
}

export function ProjectsPicker({ projects, selectedIds, onToggle }: ProjectsPickerProps) {
  return (
    <div className="grid gap-2 sm:grid-cols-2">
      {projects.map((proj) => {
        const isSelected = selectedIds.has(proj.id)
        return (
          <button
            key={proj.id}
            type="button"
            onClick={() => onToggle(proj.id)}
            className={cn(
              "text-left rounded-lg border p-3 transition-colors",
              isSelected
                ? "border-primary bg-primary/8"
                : "border-border bg-background hover:bg-muted/50"
            )}
          >
            <p className="text-sm font-medium leading-tight mb-1">{proj.name}</p>
            <p className="text-xs text-muted-foreground leading-snug">{proj.tech_stack}</p>
            {proj.bullets[0] && (
              <p className="text-xs text-muted-foreground mt-1.5 line-clamp-2">
                {proj.bullets[0]}
              </p>
            )}
          </button>
        )
      })}
    </div>
  )
}
