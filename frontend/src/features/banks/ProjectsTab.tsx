import { useState } from "react"
import { toast } from "sonner"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import {
  useProjects,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
  type Project,
} from "@/hooks/useBanks"
import { CRUDList } from "./CRUDList"

function ProjectForm({
  item,
  onSave,
  onCancel,
}: {
  item: Project | null
  onSave: () => void
  onCancel: () => void
}) {
  const [name, setName] = useState(item?.name ?? "")
  const [description, setDescription] = useState(item?.description ?? "")
  const [techStack, setTechStack] = useState(item?.tech_stack ?? "")
  const [bullets, setBullets] = useState((item?.bullets ?? []).join("\n"))
  const [githubUrl, setGithubUrl] = useState(item?.github_url ?? "")

  const createProject = useCreateProject()
  const updateProject = useUpdateProject()
  const isPending = createProject.isPending || updateProject.isPending

  function handleSave() {
    const payload = {
      name,
      description: description.trim() || undefined,
      tech_stack: techStack,
      bullets: bullets.split("\n").map((l) => l.trim()).filter(Boolean),
      github_url: githubUrl || undefined,
    }
    if (item) {
      updateProject.mutate({ id: item.id, ...payload }, {
        onSuccess: () => { toast.success("Project updated"); onSave() },
        onError: () => toast.error("Failed to update project"),
      })
    } else {
      createProject.mutate(payload, {
        onSuccess: () => { toast.success("Project added"); onSave() },
        onError: () => toast.error("Failed to add project"),
      })
    }
  }

  return (
    <div className="space-y-3">
      <div className="grid sm:grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label>Name</Label>
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Project name" />
        </div>
        <div className="space-y-1">
          <Label>Tech Stack</Label>
          <Input value={techStack} onChange={(e) => setTechStack(e.target.value)} placeholder="React, FastAPI, …" />
        </div>
      </div>
      <div className="space-y-1">
        <Label>Description <span className="text-muted-foreground text-xs">(1-2 sentences — what it is, what domain, what it demonstrates)</span></Label>
        <Textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={2} className="resize-none text-sm" placeholder="e.g. Full-stack AI scheduling tool for university students, demonstrating LLM integration, multi-step reasoning, and production deployment." />
      </div>
      <div className="space-y-1">
        <Label>Bullets <span className="text-muted-foreground text-xs">(one per line)</span></Label>
        <Textarea value={bullets} onChange={(e) => setBullets(e.target.value)} rows={4} className="resize-none text-sm" />
      </div>
      <div className="space-y-1">
        <Label>GitHub URL <span className="text-muted-foreground text-xs">(optional)</span></Label>
        <Input value={githubUrl} onChange={(e) => setGithubUrl(e.target.value)} placeholder="https://github.com/..." />
      </div>
      <div className="flex gap-2 justify-end">
        <Button variant="ghost" size="sm" onClick={onCancel}>Cancel</Button>
        <Button size="sm" onClick={handleSave} disabled={isPending || !name.trim()}>
          {isPending ? "Saving…" : "Save"}
        </Button>
      </div>
    </div>
  )
}

export function ProjectsTab() {
  const { data: projects = [], isLoading } = useProjects()
  const deleteProject = useDeleteProject()

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>

  const listItems = projects.map((p) => ({
    ...p,
    label: p.name,
    sublabel: p.tech_stack,
  }))

  return (
    <CRUDList
      items={listItems}
      renderForm={(item, onSave, onCancel) => (
        <ProjectForm item={item} onSave={onSave} onCancel={onCancel} />
      )}
      onDelete={(id) =>
        deleteProject.mutate(id, {
          onSuccess: () => toast.success("Project deleted"),
          onError: () => toast.error("Failed to delete"),
        })
      }
      emptyMessage="No projects yet. Add one to get started."
    />
  )
}
