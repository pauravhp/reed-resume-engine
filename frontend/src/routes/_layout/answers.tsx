import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/answers")({
  component: AnswersPage,
})

function AnswersPage() {
  return <div>Answers</div>
}
