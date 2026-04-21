import { Copy } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { buildLatex, type LatexInput } from "@/utils/latex"

interface CopyLatexButtonProps {
  latexInput: LatexInput
  disabled?: boolean
}

export function CopyLatexButton({ latexInput, disabled }: CopyLatexButtonProps) {
  async function handleCopy() {
    const latex = buildLatex(latexInput)
    await navigator.clipboard.writeText(latex)
    toast.success("LaTeX copied to clipboard", {
      duration: 2000,
      style: {
        background: "oklch(94% 0.060 145)",
        color: "oklch(28% 0.12 145)",
        border: "1px solid oklch(78% 0.10 145)",
      },
    })
  }

  return (
    <Button
      onClick={handleCopy}
      disabled={disabled}
      className="w-full gap-2"
      variant="outline"
    >
      <Copy className="h-4 w-4" />
      Copy LaTeX
    </Button>
  )
}
