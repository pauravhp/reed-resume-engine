import { useEffect, useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { apiGet, apiPut } from "@/lib/api"

interface ProfileData {
  bio_context: string | null
  groq_api_key_set: boolean
  phone: string | null
  linkedin_url: string | null
  github_url: string | null
}

interface ProfileUpdate {
  bio_context?: string
  groq_api_key?: string
  phone?: string
  linkedin_url?: string
  github_url?: string
}

export function ProfileForm() {
  const queryClient = useQueryClient()

  const { data: profile, isLoading } = useQuery<ProfileData>({
    queryKey: ["profile"],
    queryFn: () => apiGet("/api/v1/profile/"),
  })

  const [bioContext, setBioContext] = useState("")
  const [groqKey, setGroqKey] = useState("")
  const [phone, setPhone] = useState("")
  const [linkedinUrl, setLinkedinUrl] = useState("")
  const [githubUrl, setGithubUrl] = useState("")

  useEffect(() => {
    if (profile) {
      setBioContext(profile.bio_context ?? "")
      setPhone(profile.phone ?? "")
      setLinkedinUrl(profile.linkedin_url ?? "")
      setGithubUrl(profile.github_url ?? "")
    }
  }, [profile])

  const saveMutation = useMutation({
    mutationFn: (update: ProfileUpdate) => apiPut("/api/v1/profile/", update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] })
      toast.success("Profile saved")
    },
    onError: () => toast.error("Failed to save profile"),
  })

  function handleSave() {
    const update: ProfileUpdate = {
      bio_context: bioContext,
      phone,
      linkedin_url: linkedinUrl,
      github_url: githubUrl,
    }
    if (groqKey.trim()) update.groq_api_key = groqKey.trim()
    saveMutation.mutate(update)
  }

  if (isLoading) return <p className="text-muted-foreground text-sm">Loading…</p>

  return (
    <div className="max-w-lg space-y-8">
      <section className="space-y-3">
        <h2 className="font-semibold text-sm tracking-wide uppercase text-muted-foreground">
          Contact
        </h2>
        <div className="space-y-2.5">
          <div className="space-y-1">
            <Label>Phone</Label>
            <Input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+1 (555) 000-0000" />
          </div>
          <div className="space-y-1">
            <Label>LinkedIn URL</Label>
            <Input value={linkedinUrl} onChange={(e) => setLinkedinUrl(e.target.value)} placeholder="https://linkedin.com/in/..." />
          </div>
          <div className="space-y-1">
            <Label>GitHub URL</Label>
            <Input value={githubUrl} onChange={(e) => setGithubUrl(e.target.value)} placeholder="https://github.com/..." />
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="font-semibold text-sm tracking-wide uppercase text-muted-foreground">
          Bio Context
        </h2>
        <Textarea
          value={bioContext}
          onChange={(e) => setBioContext(e.target.value)}
          rows={5}
          placeholder="Describe your background, strengths, and career goals. The AI uses this for summary generation."
          className="resize-none text-sm"
        />
      </section>

      <section className="space-y-3">
        <div className="flex items-center gap-2">
          <h2 className="font-semibold text-sm tracking-wide uppercase text-muted-foreground">
            Groq API Key
          </h2>
          {profile?.groq_api_key_set && (
            <Badge variant="secondary" className="text-xs">Key saved</Badge>
          )}
        </div>
        <Input
          type="password"
          value={groqKey}
          onChange={(e) => setGroqKey(e.target.value)}
          placeholder={profile?.groq_api_key_set ? "Enter new key to replace…" : "gsk_..."}
        />
        <p className="text-xs text-muted-foreground">
          Required for resume generation. Get yours at console.groq.com.
        </p>
      </section>

      <Button onClick={handleSave} disabled={saveMutation.isPending}>
        {saveMutation.isPending ? "Saving…" : "Save Profile"}
      </Button>
    </div>
  )
}
