import { useState } from "react"
import { toast } from "sonner"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { MessageSquare } from "lucide-react"
import { AIOutputCard } from "@/features/generate/AIOutputCard/AIOutputCard"
import { useAnswers } from "@/hooks/useAnswers"

export function AnswersPage() {
  const [jd, setJd] = useState("")
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState<string | null>(null)
  const mutation = useAnswers()

  function handleGenerate() {
    mutation.mutate(
      { jd_text: jd, question },
      {
        onSuccess: (data) => setAnswer(data.answer),
        onError: () => toast.error("Failed to generate answer. Check your Groq API key."),
      }
    )
  }

  function handleRegenerate() {
    handleGenerate()
  }

  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <div className="space-y-3">
        <div className="space-y-1">
          <Label>Job Description</Label>
          <Textarea
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            rows={6}
            placeholder="Paste the job description…"
            className="resize-none text-sm"
          />
        </div>
        <div className="space-y-1">
          <Label>Question</Label>
          <Input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Why are you a good fit for this role?"
          />
        </div>
        <Button
          onClick={handleGenerate}
          disabled={!jd.trim() || !question.trim() || mutation.isPending}
          className="gap-2"
        >
          <MessageSquare className="h-4 w-4" />
          {mutation.isPending ? "Generating…" : "Generate Answer"}
        </Button>
      </div>

      {answer !== null && (
        <AIOutputCard
          title="Answer"
          onRegenerate={handleRegenerate}
          isRegenerating={mutation.isPending}
        >
          <Textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            rows={8}
            className="resize-none text-sm"
          />
        </AIOutputCard>
      )}
    </div>
  )
}
