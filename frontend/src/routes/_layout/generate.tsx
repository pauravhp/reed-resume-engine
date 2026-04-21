import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/generate")({
  component: GeneratePage,
})

function GeneratePage() {
  return <div>Generate</div>
}
