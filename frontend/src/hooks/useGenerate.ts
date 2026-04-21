import { useMutation } from "@tanstack/react-query"
import { apiPost } from "@/lib/api"

export interface ExperienceOutput {
  company: string
  role_title: string
  start_date: string
  end_date: string | null
  location: string
  bullets: string[]
}

export interface ProjectOutput {
  id: string
  name: string
  tech_stack: string
  bullets: string[]
  github_url: string | null
}

export interface SkillsOutput {
  languages: string
  frameworks: string
  tools: string
}

export interface GenerateOutput {
  id: string
  match_score: number
  match_reasoning: string
  summary: string
  experiences: ExperienceOutput[]
  projects: ProjectOutput[]
  skills: SkillsOutput
}

export function useGenerate() {
  return useMutation({
    mutationFn: (jd_text: string) =>
      apiPost<GenerateOutput>("/api/v1/resumes/generate", { jd_text }),
  })
}
