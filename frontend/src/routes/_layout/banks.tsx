import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/banks")({
  component: BanksPage,
})

function BanksPage() {
  return <div>Banks</div>
}
