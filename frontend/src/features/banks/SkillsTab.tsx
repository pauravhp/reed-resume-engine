import { useEffect, useState } from "react"
import { toast } from "sonner"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { useSkills, useUpsertSkills } from "@/hooks/useBanks"

export function SkillsTab() {
  const { data: skills, isLoading } = useSkills()
  const upsert = useUpsertSkills()
  const [languages, setLanguages] = useState("")
  const [frameworks, setFrameworks] = useState("")
  const [tools, setTools] = useState("")

  useEffect(() => {
    if (skills) {
      setLanguages((skills.languages ?? []).join(", "))
      setFrameworks((skills.frameworks ?? []).join(", "))
      setTools((skills.tools ?? []).join(", "))
    }
  }, [skills])

  function handleSave() {
    const toList = (s: string) => s.split(",").map((x) => x.trim()).filter(Boolean)
    upsert.mutate(
      { languages: toList(languages), frameworks: toList(frameworks), tools: toList(tools) },
      {
        onSuccess: () => toast.success("Skills saved"),
        onError: () => toast.error("Failed to save skills"),
      }
    )
  }

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>

  return (
    <div className="max-w-lg space-y-3">
      {([
        ["languages",  "Languages",           "Python, TypeScript, Go, …"],
        ["frameworks", "Frameworks / Libraries","React, FastAPI, SQLModel, …"],
        ["tools",      "Tools",                "Docker, Git, PostgreSQL, …"],
      ] as const).map(([field, label, placeholder]) => (
        <div key={field} className="space-y-1">
          <Label>{label}</Label>
          <Input
            value={field === "languages" ? languages : field === "frameworks" ? frameworks : tools}
            onChange={(e) => {
              if (field === "languages") setLanguages(e.target.value)
              else if (field === "frameworks") setFrameworks(e.target.value)
              else setTools(e.target.value)
            }}
            placeholder={placeholder}
          />
        </div>
      ))}
      <Button onClick={handleSave} disabled={upsert.isPending}>
        {upsert.isPending ? "Saving…" : "Save Skills"}
      </Button>
    </div>
  )
}
