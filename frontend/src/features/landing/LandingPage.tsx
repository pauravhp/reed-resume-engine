import { Link } from "@tanstack/react-router"

const FEATURES = [
  {
    title: "Generate",
    description: "Paste a job description and get a tailored LaTeX resume in seconds, powered by Groq.",
  },
  {
    title: "Track",
    description: "Log every application, update status through the pipeline, and keep notes inline.",
  },
  {
    title: "Answer",
    description: "Get AI-crafted answers to interview questions, grounded in the job description.",
  },
]

export function LandingPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex items-center justify-between px-8 py-5">
        <span className="font-display font-bold text-lg tracking-tight">Reed</span>
        <div className="flex gap-3">
          <Link
            to="/login"
            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
          >
            Log In
          </Link>
          <Link
            to="/signup"
            className="text-sm font-medium bg-primary text-primary-foreground px-4 py-1.5 rounded-md hover:opacity-90 transition-opacity"
          >
            Sign Up
          </Link>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20">
        <h1 className="font-display text-5xl font-bold tracking-tight leading-tight max-w-2xl mb-4">
          Resumes tailored to every job, in seconds.
        </h1>
        <p className="text-muted-foreground text-lg max-w-md mb-10">
          Paste a job description. Reed generates a LaTeX resume matched to the role, from your own experience bank.
        </p>
        <Link
          to="/signup"
          className="bg-primary text-primary-foreground font-medium px-8 py-3 rounded-md hover:opacity-90 transition-opacity"
        >
          Get Started
        </Link>

        <div className="grid sm:grid-cols-3 gap-6 mt-20 max-w-3xl text-left">
          {FEATURES.map((f) => (
            <div key={f.title} className="bg-card rounded-lg border p-5">
              <h3 className="font-display font-semibold mb-1.5">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.description}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
