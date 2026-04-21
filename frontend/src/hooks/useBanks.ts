import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { apiDelete, apiGet, apiPost, apiPut } from "@/lib/api"

// ---- Types ----

export interface Project {
  id: string
  name: string
  tech_stack: string
  bullets: string[]
  github_url: string | null
}
export interface ProjectCreate { name: string; tech_stack: string; bullets: string[]; github_url?: string }
export interface ProjectUpdate extends ProjectCreate { id: string }

export interface Experience {
  id: string
  company: string
  role_title: string
  start_date: string
  end_date: string | null
  location: string
  bullets: string[]
}
export interface ExperienceCreate { company: string; role_title: string; start_date: string; end_date?: string | null; location: string; bullets: string[] }
export interface ExperienceUpdate extends ExperienceCreate { id: string }

export interface Education {
  institution: string | null
  degree: string | null
  field_of_study: string | null
  start_date: string | null
  end_date: string | null
  location: string | null
  gpa: string | null
  coursework: string[]
}

export interface Leadership {
  id: string
  organization: string
  role_title: string
  start_date: string
  end_date: string | null
  location: string
  bullets: string[]
}
export interface LeadershipCreate { organization: string; role_title: string; start_date: string; end_date?: string | null; location: string; bullets: string[] }
export interface LeadershipUpdate extends LeadershipCreate { id: string }

export interface Skills {
  languages: string
  frameworks: string
  tools: string
}

// ---- Projects ----

export function useProjects() {
  return useQuery<Project[]>({
    queryKey: ["projects"],
    queryFn: () => apiGet<{ data: Project[] }>("/api/v1/projects/").then((r) => r.data),
  })
}

export function useCreateProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: ProjectCreate) => apiPost<Project>("/api/v1/projects/", body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  })
}

export function useUpdateProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...body }: ProjectUpdate) => apiPut<Project>(`/api/v1/projects/${id}`, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  })
}

export function useDeleteProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiDelete(`/api/v1/projects/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  })
}

// ---- Experiences ----

export function useExperiences() {
  return useQuery<Experience[]>({
    queryKey: ["experiences"],
    queryFn: () => apiGet<{ data: Experience[] }>("/api/v1/experiences/").then((r) => r.data),
  })
}

export function useCreateExperience() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: ExperienceCreate) => apiPost<Experience>("/api/v1/experiences/", body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["experiences"] }),
  })
}

export function useUpdateExperience() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...body }: ExperienceUpdate) => apiPut<Experience>(`/api/v1/experiences/${id}`, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["experiences"] }),
  })
}

export function useDeleteExperience() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiDelete(`/api/v1/experiences/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["experiences"] }),
  })
}

// ---- Education ----

export function useEducation() {
  return useQuery<Education | null>({
    queryKey: ["education"],
    queryFn: () => apiGet("/api/v1/education/"),
  })
}

export function useUpsertEducation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: Education) => apiPut<Education>("/api/v1/education/", body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["education"] }),
  })
}

// ---- Leadership ----

export function useLeadership() {
  return useQuery<Leadership[]>({
    queryKey: ["leadership"],
    queryFn: () => apiGet<{ data: Leadership[] }>("/api/v1/leadership/").then((r) => r.data),
  })
}

export function useCreateLeadership() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: LeadershipCreate) => apiPost<Leadership>("/api/v1/leadership/", body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["leadership"] }),
  })
}

export function useUpdateLeadership() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, ...body }: LeadershipUpdate) => apiPut<Leadership>(`/api/v1/leadership/${id}`, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["leadership"] }),
  })
}

export function useDeleteLeadership() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiDelete(`/api/v1/leadership/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["leadership"] }),
  })
}

// ---- Skills ----

export function useSkills() {
  return useQuery<Skills | null>({
    queryKey: ["skills"],
    queryFn: () => apiGet("/api/v1/skills/"),
  })
}

export function useUpsertSkills() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: Skills) => apiPut<Skills>("/api/v1/skills/", body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["skills"] }),
  })
}
