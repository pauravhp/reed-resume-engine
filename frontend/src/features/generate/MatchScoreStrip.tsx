interface MatchScoreStripProps {
  score: number
  reasoning: string
}

export function MatchScoreStrip({ score, reasoning }: MatchScoreStripProps) {
  const color =
    score >= 75 ? "bg-green-500" : score >= 50 ? "bg-yellow-500" : "bg-red-400"

  return (
    <div className="rounded-lg border bg-card px-4 py-3">
      <div className="flex items-center gap-3 mb-1.5">
        <span className="text-sm font-semibold">Match Score</span>
        <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${color}`}
            style={{ width: `${score}%` }}
          />
        </div>
        <span className="text-sm font-semibold tabular-nums">{score}%</span>
      </div>
      <p className="text-xs text-muted-foreground leading-snug">{reasoning}</p>
    </div>
  )
}
