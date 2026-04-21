import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const STATUS_OPTIONS = [
  { value: "not_applied",       label: "Not Applied"       },
  { value: "applied",           label: "Applied"           },
  { value: "response_received", label: "Response Received" },
  { value: "interview",         label: "Interview"         },
  { value: "rejected",          label: "Rejected"          },
  { value: "offer",             label: "Offer"             },
]

interface StatusSelectProps {
  value: string
  onChange: (value: string) => void
}

export function StatusSelect({ value, onChange }: StatusSelectProps) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="h-8 text-xs w-[150px]">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {STATUS_OPTIONS.map((opt) => (
          <SelectItem key={opt.value} value={opt.value} className="text-xs">
            {opt.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
