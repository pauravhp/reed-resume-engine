import { Link } from "@tanstack/react-router"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { apiGet, apiPatch } from "@/lib/api"
import { StatusSelect } from "./StatusSelect"
import { NotesCell } from "./NotesCell"
import { Button } from "@/components/ui/button"
import { Zap } from "lucide-react"

interface Application {
  id: string
  company: string | null
  role_title: string | null
  match_score: number | null
  status: string
  notes: string | null
  created_at: string
}

export function ApplicationsTable() {
  const qc = useQueryClient()

  const { data, isLoading } = useQuery<{ data: Application[] }>({
    queryKey: ["applications"],
    queryFn: () => apiGet("/api/v1/applications/"),
  })

  const patchMutation = useMutation({
    mutationFn: ({ id, update }: {
      id: string
      update: { status?: string; notes?: string; company?: string | null; role_title?: string | null }
    }) => apiPatch(`/api/v1/applications/${id}`, update),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["applications"] }),
  })

  if (isLoading) return <p className="text-sm text-muted-foreground">Loading…</p>

  const applications = data?.data ?? []

  if (applications.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <p className="text-muted-foreground text-sm mb-4">
          No applications yet. Generate your first resume to get started.
        </p>
        <Button asChild variant="outline" size="sm" className="gap-2">
          <Link to="/generate">
            <Zap className="h-4 w-4" />
            Generate Resume
          </Link>
        </Button>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b bg-muted/40">
            <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Company</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Role</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Match</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Status</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Date</th>
            <th className="px-4 py-3 text-left text-xs font-medium text-muted-foreground">Notes</th>
          </tr>
        </thead>
        <tbody>
          {applications.map((app) => (
            <tr key={app.id} className="border-b last:border-0 hover:bg-muted/20">
              <td className="px-4 py-3 font-medium min-w-[140px]">
                <NotesCell
                  value={app.company ?? ""}
                  onSave={(company) =>
                    patchMutation.mutate({ id: app.id, update: { company: company || null } })
                  }
                  placeholder="Click to add company"
                />
              </td>
              <td className="px-4 py-3 text-muted-foreground min-w-[140px]">
                <NotesCell
                  value={app.role_title ?? ""}
                  onSave={(role_title) =>
                    patchMutation.mutate({ id: app.id, update: { role_title: role_title || null } })
                  }
                  placeholder="Click to add role"
                />
              </td>
              <td className="px-4 py-3 tabular-nums">
                {app.match_score !== null ? `${app.match_score}%` : "—"}
              </td>
              <td className="px-4 py-3">
                <StatusSelect
                  value={app.status}
                  onChange={(status) =>
                    patchMutation.mutate({ id: app.id, update: { status } })
                  }
                />
              </td>
              <td className="px-4 py-3 text-muted-foreground text-xs whitespace-nowrap">
                {new Date(app.created_at).toLocaleDateString()}
              </td>
              <td className="px-4 py-3 min-w-[160px]">
                <NotesCell
                  value={app.notes ?? ""}
                  onSave={(notes) =>
                    patchMutation.mutate({ id: app.id, update: { notes } })
                  }
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
