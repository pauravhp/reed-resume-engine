import { useState } from "react"
import { Plus, Trash2, ChevronDown, ChevronUp } from "lucide-react"
import { Button } from "@/components/ui/button"

export interface CRUDListItem {
  id: string
  label: string
  sublabel?: string
}

interface CRUDListProps<T extends CRUDListItem> {
  items: T[]
  renderForm: (item: T | null, onSave: () => void, onCancel: () => void) => React.ReactNode
  onDelete: (id: string) => void
  isDeleting?: boolean
  emptyMessage?: string
}

export function CRUDList<T extends CRUDListItem>({
  items,
  renderForm,
  onDelete,
  emptyMessage = "Nothing here yet.",
}: CRUDListProps<T>) {
  const [expandedId, setExpandedId] = useState<string | "new" | null>(null)

  return (
    <div className="space-y-2">
      <Button
        variant="outline"
        size="sm"
        className="gap-1.5"
        onClick={() => setExpandedId(expandedId === "new" ? null : "new")}
      >
        <Plus className="h-3.5 w-3.5" />
        Add
      </Button>

      {expandedId === "new" && (
        <div className="rounded-lg border bg-card p-4">
          {renderForm(null, () => setExpandedId(null), () => setExpandedId(null))}
        </div>
      )}

      {items.length === 0 && expandedId !== "new" && (
        <p className="text-sm text-muted-foreground py-4">{emptyMessage}</p>
      )}

      {items.map((item) => (
        <div key={item.id} className="rounded-lg border bg-card overflow-hidden">
          <button
            type="button"
            className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-muted/40 transition-colors"
            onClick={() => setExpandedId(expandedId === item.id ? null : item.id)}
          >
            <div>
              <p className="text-sm font-medium">{item.label}</p>
              {item.sublabel && (
                <p className="text-xs text-muted-foreground">{item.sublabel}</p>
              )}
            </div>
            {expandedId === item.id ? (
              <ChevronUp className="h-4 w-4 text-muted-foreground shrink-0" />
            ) : (
              <ChevronDown className="h-4 w-4 text-muted-foreground shrink-0" />
            )}
          </button>

          {expandedId === item.id && (
            <div className="px-4 pb-4 pt-1 border-t">
              {renderForm(
                item,
                () => setExpandedId(null),
                () => setExpandedId(null)
              )}
              <div className="flex justify-end mt-3">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-destructive hover:text-destructive gap-1.5"
                  onClick={() => { onDelete(item.id); setExpandedId(null) }}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Delete
                </Button>
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
