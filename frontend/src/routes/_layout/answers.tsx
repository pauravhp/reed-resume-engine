import { createFileRoute } from "@tanstack/react-router"
import { AnswersPage } from "@/features/answers/AnswersPage"

export const Route = createFileRoute("/_layout/answers")({
  component: AnswersRoute,
  head: () => ({ meta: [{ title: "Answers — Reed" }] }),
})

function AnswersRoute() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Tailored Answer</h1>
        <p className="text-muted-foreground text-sm mt-0.5">
          Paste a job description and question to get a tailored interview answer.
        </p>
      </div>
      <AnswersPage />
    </div>
  )
}
