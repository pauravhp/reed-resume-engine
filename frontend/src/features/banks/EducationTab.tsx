import { useState } from "react"
import { toast } from "sonner"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import {
  useEducations,
  useCreateEducation,
  useUpdateEducation,
  useDeleteEducation,
  type EducationItem,
} from "@/hooks/useBanks"
import { CRUDList } from "./CRUDList"

function EducationForm({
  item,
  onSave,
  onCancel,
}: {
  item: EducationItem | null
  onSave: () => void
  onCancel: () => void
}) {
  const [institution, setInstitution] = useState(item?.institution ?? "")
  const [degree, setDegree] = useState(item?.degree ?? "")
  const [fieldOfStudy, setFieldOfStudy] = useState(item?.field_of_study ?? "")
  const [startDate, setStartDate] = useState(item?.start_date ?? "")
  const [endDate, setEndDate] = useState(item?.end_date ?? "")
  const [location, setLocation] = useState(item?.location ?? "")
  const [gpa, setGpa] = useState(item?.gpa ?? "")
  const [coursework, setCoursework] = useState((item?.coursework ?? []).join(", "))

  const createEdu = useCreateEducation()
  const updateEdu = useUpdateEducation()
  const isPending = createEdu.isPending || updateEdu.isPending

  function handleSave() {
    const payload = {
      institution,
      degree,
      field_of_study: fieldOfStudy,
      start_date: startDate,
      end_date: endDate,
      location: location || null,
      gpa: gpa || null,
      coursework: coursework.split(",").map((s) => s.trim()).filter(Boolean),
    }
    if (item) {
      updateEdu.mutate({ id: item.id, ...payload }, {
        onSuccess: () => { toast.success("Education updated"); onSave() },
        onError: () => toast.error("Failed to update"),
      })
    } else {
      createEdu.mutate(payload, {
        onSuccess: () => { toast.success("Education added"); onSave() },
        onError: () => toast.error("Failed to add"),
      })
    }
  }

  return (
    <div className="space-y-3">
      <div className="grid sm:grid-cols-2 gap-3">
        <div className="space-y-1 sm:col-span-2">
          <Label>Institution</Label>
          <Input value={institution} onChange={(e) => setInstitution(e.target.value)} placeholder="University of Victoria" />
        </div>
        <div className="space-y-1">
          <Label>Degree</Label>
          <Input value={degree} onChange={(e) => setDegree(e.target.value)} placeholder="Bachelor of Science" />
        </div>
        <div className="space-y-1">
          <Label>Field of Study</Label>
          <Input value={fieldOfStudy} onChange={(e) => setFieldOfStudy(e.target.value)} placeholder="Computer Science" />
        </div>
        <div className="space-y-1">
          <Label>Start Date</Label>
          <Input value={startDate} onChange={(e) => setStartDate(e.target.value)} placeholder="Sep 2021" />
        </div>
        <div className="space-y-1">
          <Label>End Date <span className="text-muted-foreground text-xs">(blank = Present)</span></Label>
          <Input value={endDate} onChange={(e) => setEndDate(e.target.value)} placeholder="Dec 2025" />
        </div>
        <div className="space-y-1">
          <Label>Location <span className="text-muted-foreground text-xs">(optional)</span></Label>
          <Input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Victoria, BC" />
        </div>
        <div className="space-y-1">
          <Label>GPA <span className="text-muted-foreground text-xs">(optional)</span></Label>
          <Input value={gpa} onChange={(e) => setGpa(e.target.value)} placeholder="3.8" />
        </div>
        <div className="space-y-1 sm:col-span-2">
          <Label>Coursework / Honours <span className="text-muted-foreground text-xs">(comma-separated)</span></Label>
          <Input
            value={coursework}
            onChange={(e) => setCoursework(e.target.value)}
            placeholder="Algorithms, Distributed Systems, Honours in GPU Computing (96%, A+)"
          />
        </div>
      </div>
      <div className="flex gap-2 justify-end">
        <Button variant="ghost" size="sm" onClick={onCancel}>Cancel</Button>
        <Button size="sm" onClick={handleSave} disabled={isPending || !institution.trim()}>
          {isPending ? "Saving…" : "Save"}
        </Button>
      </div>
    </div>
  )
}

export function EducationTab() {
  const { data: educations = [], isLoading } = useEducations()
  const deleteEdu = useDeleteEducation()

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>

  const listItems = educations.map((e) => ({
    ...e,
    label: e.institution,
    sublabel: `${e.degree} in ${e.field_of_study} · ${e.start_date} – ${e.end_date || "Present"}`,
  }))

  return (
    <CRUDList
      items={listItems}
      renderForm={(item, onSave, onCancel) => (
        <EducationForm item={item} onSave={onSave} onCancel={onCancel} />
      )}
      onDelete={(id) =>
        deleteEdu.mutate(id, {
          onSuccess: () => toast.success("Education deleted"),
          onError: () => toast.error("Failed to delete"),
        })
      }
      emptyMessage="No education entries yet."
    />
  )
}
