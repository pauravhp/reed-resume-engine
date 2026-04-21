import { createFileRoute } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { toast } from "sonner"

import { JDInputSection } from "@/features/generate/JDInputSection"
import { MatchScoreStrip } from "@/features/generate/MatchScoreStrip"
import { CopyLatexButton } from "@/features/generate/CopyLatexButton"
import { AIOutputCard } from "@/features/generate/AIOutputCard/AIOutputCard"
import { SummaryEditor } from "@/features/generate/AIOutputCard/SummaryEditor"
import { ExperienceEditor } from "@/features/generate/AIOutputCard/ExperienceEditor"
import { ProjectsPicker } from "@/features/generate/AIOutputCard/ProjectsPicker"
import { SkillsEditor } from "@/features/generate/AIOutputCard/SkillsEditor"
import { useGenerate, type GenerateOutput } from "@/hooks/useGenerate"
import {
  useRegenerateSummary,
  useRegenerateExperiences,
  useRegenerateProjects,
} from "@/hooks/useRegenerate"
import useAuth from "@/hooks/useAuth"
import { apiGet } from "@/lib/api"

export const Route = createFileRoute("/_layout/generate")({
  component: GeneratePage,
  head: () => ({ meta: [{ title: "Generate — Reed" }] }),
})

function GeneratePage() {
  const { user } = useAuth()
  const [jd, setJd] = useState(() => localStorage.getItem("jd_capture") ?? "")
  const [output, setOutput] = useState<GenerateOutput | null>(null)

  const [summary, setSummary] = useState("")
  const [checkedBullets, setCheckedBullets] = useState<Set<string>>(new Set())
  const [selectedProjectIds, setSelectedProjectIds] = useState<Set<string>>(new Set())
  const [skills, setSkills] = useState({ languages: "", frameworks: "", tools: "" })

  useEffect(() => {
    if (localStorage.getItem("jd_capture")) {
      localStorage.removeItem("jd_capture")
    }
  }, [])

  const { data: profile } = useQuery<{
    phone: string | null
    linkedin_url: string | null
    github_url: string | null
  }>({
    queryKey: ["profile"],
    queryFn: () => apiGet("/api/v1/profile/"),
  })

  const generateMutation = useGenerate()
  const regenSummary = useRegenerateSummary(output?.id ?? "")
  const regenExperiences = useRegenerateExperiences(output?.id ?? "")
  const regenProjects = useRegenerateProjects(output?.id ?? "")

  function applyOutput(data: GenerateOutput) {
    setOutput(data)
    setSummary(data.summary)
    const allBullets = new Set(data.experiences.flatMap((e) => e.bullets))
    setCheckedBullets(allBullets)
    setSelectedProjectIds(new Set(data.projects.map((p) => p.id)))
    setSkills(data.skills)
  }

  function handleGenerate() {
    generateMutation.mutate(jd, {
      onSuccess: applyOutput,
      onError: () => toast.error("Generation failed. Check your Groq API key in Profile."),
    })
  }

  function handleToggleBullet(bullet: string, checked: boolean) {
    setCheckedBullets((prev) => {
      const next = new Set(prev)
      if (checked) next.add(bullet)
      else next.delete(bullet)
      return next
    })
  }

  function handleToggleProject(id: string) {
    setSelectedProjectIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const latexInput = output
    ? {
        fullName: user?.full_name ?? "",
        phone: profile?.phone ?? "",
        linkedinUrl: profile?.linkedin_url ?? "",
        githubUrl: profile?.github_url ?? "",
        summary,
        experiences: (output.experiences ?? []).map((exp) => ({
          ...exp,
          bullets: exp.bullets.filter((b) => checkedBullets.has(b)),
        })),
        projects: (output.projects ?? []).filter((p) => selectedProjectIds.has(p.id)),
        skills,
      }
    : null

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Generate Resume</h1>
        <p className="text-muted-foreground text-sm mt-0.5">
          Paste a job description and get a tailored LaTeX resume.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-[2fr_3fr]">
        <JDInputSection
          value={jd}
          onChange={setJd}
          onGenerate={handleGenerate}
          isLoading={generateMutation.isPending}
        />

        {output && (
          <div className="flex flex-col gap-4">
            <MatchScoreStrip
              score={output.match_score}
              reasoning={output.match_reasoning}
            />

            <AIOutputCard
              title="Summary"
              onRegenerate={() =>
                regenSummary.mutate(undefined, {
                  onSuccess: (data) => setSummary(data.summary),
                })
              }
              isRegenerating={regenSummary.isPending}
            >
              <SummaryEditor value={summary} onChange={setSummary} />
            </AIOutputCard>

            <AIOutputCard
              title="Experience"
              onRegenerate={() => {
                const unchecked = output.experiences.flatMap((e) =>
                  e.bullets.filter((b) => !checkedBullets.has(b))
                )
                regenExperiences.mutate(unchecked, {
                  onSuccess: (data) => {
                    const newBullets = new Set(data.experiences.flatMap((e) => e.bullets))
                    setCheckedBullets(newBullets)
                    setOutput((prev) => prev ? { ...prev, experiences: data.experiences } : prev)
                  },
                })
              }}
              isRegenerating={regenExperiences.isPending}
            >
              <ExperienceEditor
                experiences={output.experiences}
                checkedBullets={checkedBullets}
                onToggleBullet={handleToggleBullet}
              />
            </AIOutputCard>

            <AIOutputCard
              title="Projects"
              onRegenerate={() => {
                const excluded = output.projects
                  .filter((p) => selectedProjectIds.has(p.id))
                  .map((p) => p.id)
                regenProjects.mutate(excluded, {
                  onSuccess: (data) => {
                    setSelectedProjectIds(new Set(data.projects.map((p) => p.id)))
                    setOutput((prev) => prev ? { ...prev, projects: data.projects } : prev)
                  },
                })
              }}
              isRegenerating={regenProjects.isPending}
            >
              <ProjectsPicker
                projects={output.projects}
                selectedIds={selectedProjectIds}
                onToggle={handleToggleProject}
              />
            </AIOutputCard>

            <AIOutputCard title="Skills">
              <SkillsEditor value={skills} onChange={setSkills} />
            </AIOutputCard>

            {latexInput && (
              <CopyLatexButton latexInput={latexInput} />
            )}
          </div>
        )}
      </div>
    </div>
  )
}
