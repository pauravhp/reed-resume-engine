import { useEffect, useState } from "react"
import { toast } from "sonner"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { useEducation, useUpsertEducation } from "@/hooks/useBanks"

export function EducationTab() {
  const { data: edu, isLoading } = useEducation()
  const upsert = useUpsertEducation()

  const [institution, setInstitution] = useState("")
  const [degree, setDegree] = useState("")
  const [fieldOfStudy, setFieldOfStudy] = useState("")
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [location, setLocation] = useState("")
  const [gpa, setGpa] = useState("")
  const [coursework, setCoursework] = useState("")

  useEffect(() => {
    if (edu) {
      setInstitution(edu.institution ?? "")
      setDegree(edu.degree ?? "")
      setFieldOfStudy(edu.field_of_study ?? "")
      setStartDate(edu.start_date ?? "")
      setEndDate(edu.end_date ?? "")
      setLocation(edu.location ?? "")
      setGpa(edu.gpa ?? "")
      setCoursework((edu.coursework ?? []).join(", "))
    }
  }, [edu])

  function handleSave() {
    upsert.mutate(
      {
        institution, degree, field_of_study: fieldOfStudy,
        start_date: startDate, end_date: endDate || null,
        location, gpa: gpa || null,
        coursework: coursework.split(",").map((s) => s.trim()).filter(Boolean),
      },
      {
        onSuccess: () => toast.success("Education saved"),
        onError: () => toast.error("Failed to save education"),
      }
    )
  }

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>

  return (
    <div className="max-w-lg space-y-3">
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
          <Label>End Date</Label>
          <Input value={endDate} onChange={(e) => setEndDate(e.target.value)} placeholder="Dec 2025" />
        </div>
        <div className="space-y-1">
          <Label>Location</Label>
          <Input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Victoria, BC" />
        </div>
        <div className="space-y-1">
          <Label>GPA <span className="text-muted-foreground text-xs">(optional)</span></Label>
          <Input value={gpa} onChange={(e) => setGpa(e.target.value)} placeholder="3.8" />
        </div>
        <div className="space-y-1 sm:col-span-2">
          <Label>Coursework <span className="text-muted-foreground text-xs">(comma-separated)</span></Label>
          <Input value={coursework} onChange={(e) => setCoursework(e.target.value)} placeholder="Algorithms, Distributed Systems, …" />
        </div>
      </div>
      <Button onClick={handleSave} disabled={upsert.isPending}>
        {upsert.isPending ? "Saving…" : "Save Education"}
      </Button>
    </div>
  )
}
