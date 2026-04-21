import { useMutation } from "@tanstack/react-query"
import { apiPost } from "@/lib/api"

interface GenerateAnswerInput {
  jd_text: string
  question: string
}

export function useAnswers() {
  return useMutation({
    mutationFn: (input: GenerateAnswerInput) =>
      apiPost<{ answer: string }>("/api/v1/answers/generate", input),
  })
}
