import { createFileRoute } from "@tanstack/react-router"
import { ProfileForm } from "@/features/profile/ProfileForm"

export const Route = createFileRoute("/_layout/profile")({
  component: ProfilePage,
  head: () => ({ meta: [{ title: "Profile — Reed" }] }),
})

function ProfilePage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Profile</h1>
        <p className="text-muted-foreground text-sm mt-0.5">
          Contact info, bio context, and your Groq API key.
        </p>
      </div>
      <ProfileForm />
    </div>
  )
}
