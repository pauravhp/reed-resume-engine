import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { z } from "zod"
import { BanksPage } from "@/features/banks/BanksPage"

const searchSchema = z.object({
  tab: z.string().default("projects"),
})

export const Route = createFileRoute("/_layout/banks")({
  validateSearch: searchSchema,
  component: BanksRoute,
  head: () => ({ meta: [{ title: "Banks — Reed" }] }),
})

function BanksRoute() {
  const { tab } = Route.useSearch()
  const navigate = useNavigate({ from: Route.fullPath })

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Banks</h1>
        <p className="text-muted-foreground text-sm mt-0.5">
          Manage your projects, experience, education, leadership, and skills.
        </p>
      </div>
      <BanksPage
        tab={tab}
        onTabChange={(t) => navigate({ search: { tab: t } })}
      />
    </div>
  )
}
