import { createFileRoute } from "@tanstack/react-router"
import { ApplicationsTable } from "@/features/dashboard/ApplicationsTable"

export const Route = createFileRoute("/_layout/dashboard")({
  component: DashboardPage,
  head: () => ({ meta: [{ title: "Dashboard — Reed" }] }),
})

function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-0.5">
          Your application history, newest first.
        </p>
      </div>
      <ApplicationsTable />
    </div>
  )
}
