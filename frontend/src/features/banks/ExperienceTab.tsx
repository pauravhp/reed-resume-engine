import { useState } from "react"
import { toast } from "sonner"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import {
  useExperiences,
  useCreateExperience,
  useUpdateExperience,
  useDeleteExperience,
  type Experience,
} from "@/hooks/useBanks"
import { CRUDList } from "./CRUDList"

function ExperienceForm({
  item,
  onSave,
  onCancel,
}: {
  item: Experience | null
  onSave: () => void
  onCancel: () => void
}) {
  const [company, setCompany] = useState(item?.company ?? "")
  const [roleTitle, setRoleTitle] = useState(item?.role ?? "")
  const [startDate, setStartDate] = useState(item?.start_date ?? "")
  const [endDate, setEndDate] = useState(item?.end_date ?? "")
  const [location, setLocation] = useState(item?.location ?? "")
  const [bullets, setBullets] = useState((item?.bullets ?? []).join("\n"))

  const createExp = useCreateExperience()
  const updateExp = useUpdateExperience()
  const isPending = createExp.isPending || updateExp.isPending

  function handleSave() {
    const payload = {
      company, role: roleTitle,
      start_date: startDate, end_date: endDate || null,
      location,
      bullets: bullets.split("\n").map((l) => l.trim()).filter(Boolean),
    }
    if (item) {
      updateExp.mutate({ id: item.id, ...payload }, {
        onSuccess: () => { toast.success("Experience updated"); onSave() },
        onError: () => toast.error("Failed to update"),
      })
    } else {
      createExp.mutate(payload, {
        onSuccess: () => { toast.success("Experience added"); onSave() },
        onError: () => toast.error("Failed to add"),
      })
    }
  }

  return (
    <div className="space-y-3">
      <div className="grid sm:grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label>Company</Label>
          <Input value={company} onChange={(e) => setCompany(e.target.value)} />
        </div>
        <div className="space-y-1">
          <Label>Role Title</Label>
          <Input value={roleTitle} onChange={(e) => setRoleTitle(e.target.value)} />
        </div>
        <div className="space-y-1">
          <Label>Start Date</Label>
          <Input value={startDate} onChange={(e) => setStartDate(e.target.value)} placeholder="May 2022" />
        </div>
        <div className="space-y-1">
          <Label>End Date <span className="text-muted-foreground text-xs">(blank = Present)</span></Label>
          <Input value={endDate} onChange={(e) => setEndDate(e.target.value)} placeholder="Aug 2023" />
        </div>
        <div className="space-y-1 sm:col-span-2">
          <Label>Location</Label>
          <Input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Vancouver, BC" />
        </div>
      </div>
      <div className="space-y-1">
        <Label>Bullets <span className="text-muted-foreground text-xs">(one per line)</span></Label>
        <Textarea value={bullets} onChange={(e) => setBullets(e.target.value)} rows={4} className="resize-none text-sm" />
      </div>
      <div className="flex gap-2 justify-end">
        <Button variant="ghost" size="sm" onClick={onCancel}>Cancel</Button>
        <Button size="sm" onClick={handleSave} disabled={isPending || !company.trim()}>
          {isPending ? "Saving…" : "Save"}
        </Button>
      </div>
    </div>
  )
}

export function ExperienceTab() {
  const { data: experiences = [], isLoading } = useExperiences()
  const deleteExp = useDeleteExperience()

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>

  const listItems = experiences.map((e) => ({
    ...e,
    label: e.company,
    sublabel: e.role,
  }))

  return (
    <CRUDList
      items={listItems}
      renderForm={(item, onSave, onCancel) => (
        <ExperienceForm item={item} onSave={onSave} onCancel={onCancel} />
      )}
      onDelete={(id) =>
        deleteExp.mutate(id, {
          onSuccess: () => toast.success("Experience deleted"),
          onError: () => toast.error("Failed to delete"),
        })
      }
      emptyMessage="No experience entries yet."
    />
  )
}
