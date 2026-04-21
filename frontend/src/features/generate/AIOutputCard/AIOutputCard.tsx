import { RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface AIOutputCardProps {
  title: string
  onRegenerate?: () => void
  isRegenerating?: boolean
  children: React.ReactNode
  className?: string
}

export function AIOutputCard({
  title,
  onRegenerate,
  isRegenerating = false,
  children,
  className,
}: AIOutputCardProps) {
  return (
    <div className={cn("rounded-lg border bg-card p-4", className)}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm tracking-wide uppercase text-muted-foreground">
          {title}
        </h3>
        {onRegenerate && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onRegenerate}
            disabled={isRegenerating}
            className="h-7 px-2 text-xs gap-1.5"
          >
            <RefreshCw className={cn("h-3 w-3", isRegenerating && "animate-spin")} />
            Regenerate
          </Button>
        )}
      </div>
      <div className={cn("relative", isRegenerating && "opacity-50 pointer-events-none")}>
        {children}
      </div>
    </div>
  )
}
