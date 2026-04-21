import { useMutation } from "@tanstack/react-query"
import { apiPost } from "@/lib/api"
import type { ExperienceOutput, ProjectOutput } from "./useGenerate"

export function useRegenerateSummary(resumeId: string) {
  return useMutation({
    mutationFn: () =>
      apiPost<{ summary: string }>(`/api/v1/resumes/${resumeId}/regenerate/summary`),
  })
}

export function useRegenerateExperiences(resumeId: string) {
  return useMutation({
    mutationFn: (excluded_bullets: string[]) =>
      apiPost<{ experiences: ExperienceOutput[] }>(
        `/api/v1/resumes/${resumeId}/regenerate/experiences`,
        { excluded_bullets }
      ),
  })
}

export function useRegenerateProjects(resumeId: string) {
  return useMutation({
    mutationFn: (excluded_project_ids: string[]) =>
      apiPost<{ projects: ProjectOutput[] }>(
        `/api/v1/resumes/${resumeId}/regenerate/projects`,
        { excluded_project_ids }
      ),
  })
}
