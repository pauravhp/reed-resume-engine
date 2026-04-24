import { useState } from "react"
import { toast } from "sonner"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import {
  useLeadership,
  useCreateLeadership,
  useUpdateLeadership,
  useDeleteLeadership,
  type Leadership,
} from "@/hooks/useBanks"
import { CRUDList } from "./CRUDList"

function LeadershipForm({
  item,
  onSave,
  onCancel,
}: {
  item: Leadership | null
  onSave: () => void
  onCancel: () => void
}) {
  const [org, setOrg] = useState(item?.organization ?? "")
  const [role, setRole] = useState(item?.role ?? "")
  const [startDate, setStartDate] = useState(item?.start_date ?? "")
  const [endDate, setEndDate] = useState(item?.end_date ?? "")
  const [location, setLocation] = useState(item?.location ?? "")
  const [bullets, setBullets] = useState((item?.bullets ?? []).join("\n"))

  const create = useCreateLeadership()
  const update = useUpdateLeadership()
  const isPending = create.isPending || update.isPending

  function handleSave() {
    const payload = {
      organization: org, role,
      start_date: startDate, end_date: endDate || null,
      location,
      bullets: bullets.split("\n").map((l) => l.trim()).filter(Boolean),
    }
    if (item) {
      update.mutate({ id: item.id, ...payload }, {
        onSuccess: () => { toast.success("Updated"); onSave() },
        onError: () => toast.error("Failed to update"),
      })
    } else {
      create.mutate(payload, {
        onSuccess: () => { toast.success("Added"); onSave() },
        onError: () => toast.error("Failed to add"),
      })
    }
  }

  return (
    <div className="space-y-3">
      <div className="grid sm:grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label>Organization</Label>
          <Input value={org} onChange={(e) => setOrg(e.target.value)} />
        </div>
        <div className="space-y-1">
          <Label>Role</Label>
          <Input value={role} onChange={(e) => setRole(e.target.value)} />
        </div>
        <div className="space-y-1">
          <Label>Start Date</Label>
          <Input value={startDate} onChange={(e) => setStartDate(e.target.value)} placeholder="Sep 2022" />
        </div>
        <div className="space-y-1">
          <Label>End Date</Label>
          <Input value={endDate} onChange={(e) => setEndDate(e.target.value)} placeholder="Apr 2023" />
        </div>
        <div className="space-y-1 sm:col-span-2">
          <Label>Location</Label>
          <Input value={location} onChange={(e) => setLocation(e.target.value)} />
        </div>
      </div>
      <div className="space-y-1">
        <Label>Bullets <span className="text-muted-foreground text-xs">(one per line)</span></Label>
        <Textarea value={bullets} onChange={(e) => setBullets(e.target.value)} rows={3} className="resize-none text-sm" />
      </div>
      <div className="flex gap-2 justify-end">
        <Button variant="ghost" size="sm" onClick={onCancel}>Cancel</Button>
        <Button size="sm" onClick={handleSave} disabled={isPending || !org.trim()}>
          {isPending ? "Saving…" : "Save"}
        </Button>
      </div>
    </div>
  )
}

export function LeadershipTab() {
  const { data: items = [], isLoading } = useLeadership()
  const deleteItem = useDeleteLeadership()

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>

  const listItems = items.map((l) => ({ ...l, label: l.organization, sublabel: l.role }))

  return (
    <CRUDList
      items={listItems}
      renderForm={(item, onSave, onCancel) => (
        <LeadershipForm item={item} onSave={onSave} onCancel={onCancel} />
      )}
      onDelete={(id) =>
        deleteItem.mutate(id, {
          onSuccess: () => toast.success("Deleted"),
          onError: () => toast.error("Failed to delete"),
        })
      }
      emptyMessage="No leadership entries yet."
    />
  )
}
