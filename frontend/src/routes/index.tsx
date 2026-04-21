import { createFileRoute, redirect } from "@tanstack/react-router"
import { isLoggedIn } from "@/hooks/useAuth"
import { LandingPage } from "@/features/landing/LandingPage"

export const Route = createFileRoute("/")({
  beforeLoad: () => {
    if (isLoggedIn()) {
      throw redirect({ to: "/generate" })
    }
  },
  component: LandingPage,
  head: () => ({ meta: [{ title: "Reed — Resume Engine" }] }),
})
