import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/profile")({
  component: ProfilePage,
})

function ProfilePage() {
  return <div>Profile</div>
}
