import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ProjectsTab } from "./ProjectsTab"
import { ExperienceTab } from "./ExperienceTab"
import { EducationTab } from "./EducationTab"
import { LeadershipTab } from "./LeadershipTab"
import { SkillsTab } from "./SkillsTab"

const TABS = [
  { value: "projects",    label: "Projects",    component: <ProjectsTab /> },
  { value: "experience",  label: "Experience",  component: <ExperienceTab /> },
  { value: "education",   label: "Education",   component: <EducationTab /> },
  { value: "leadership",  label: "Leadership",  component: <LeadershipTab /> },
  { value: "skills",      label: "Skills",      component: <SkillsTab /> },
]

interface BanksPageProps {
  tab: string
  onTabChange: (tab: string) => void
}

export function BanksPage({ tab, onTabChange }: BanksPageProps) {
  return (
    <Tabs value={tab} onValueChange={onTabChange}>
      <TabsList className="mb-4">
        {TABS.map((t) => (
          <TabsTrigger key={t.value} value={t.value}>
            {t.label}
          </TabsTrigger>
        ))}
      </TabsList>
      {TABS.map((t) => (
        <TabsContent key={t.value} value={t.value}>
          {t.component}
        </TabsContent>
      ))}
    </Tabs>
  )
}
