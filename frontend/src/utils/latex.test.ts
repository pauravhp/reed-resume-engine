import { describe, it, expect } from "vitest"
import { latexEscape, buildLatex } from "./latex"

describe("latexEscape", () => {
  it("escapes backslash", () => {
    expect(latexEscape("a\\b")).toBe("a\\textbackslash{}b")
  })

  it("escapes ampersand", () => {
    expect(latexEscape("a&b")).toBe("a\\&b")
  })

  it("escapes percent", () => {
    expect(latexEscape("50%")).toBe("50\\%")
  })

  it("escapes dollar sign", () => {
    expect(latexEscape("$100")).toBe("\\$100")
  })

  it("escapes hash", () => {
    expect(latexEscape("#1")).toBe("\\#1")
  })

  it("escapes underscore", () => {
    expect(latexEscape("snake_case")).toBe("snake\\_case")
  })

  it("escapes curly braces", () => {
    expect(latexEscape("{val}")).toBe("\\{val\\}")
  })

  it("escapes tilde", () => {
    expect(latexEscape("a~b")).toBe("a\\textasciitilde{}b")
  })

  it("escapes caret", () => {
    expect(latexEscape("a^b")).toBe("a\\textasciicircum{}b")
  })

  it("passes plain text through unchanged", () => {
    expect(latexEscape("Hello World")).toBe("Hello World")
  })
})

describe("buildLatex", () => {
  const baseInput = {
    fullName: "Jane Doe",
    phone: "604-555-0100",
    linkedinUrl: "https://linkedin.com/in/janedoe",
    githubUrl: "https://github.com/janedoe",
    summary: "Software engineer with 5 years experience.",
    experiences: [
      {
        company: "Acme Corp",
        role_title: "Software Engineer",
        start_date: "Jan 2022",
        end_date: null,
        location: "Vancouver, BC",
        bullets: ["Built APIs", "Led migrations"],
      },
    ],
    projects: [
      {
        name: "Reed",
        tech_stack: "React, FastAPI",
        bullets: ["Resume generation engine"],
        github_url: "https://github.com/user/reed",
      },
    ],
    skills: {
      languages: "Python, TypeScript",
      frameworks: "React, FastAPI",
      tools: "Docker, Git",
    },
  }

  it("includes the full name in output", () => {
    const result = buildLatex(baseInput)
    expect(result).toContain("Jane Doe")
  })

  it("shows Present when end_date is null", () => {
    const result = buildLatex(baseInput)
    expect(result).toContain("Jan 2022 -- Present")
  })

  it("shows date range when end_date is set", () => {
    const input = {
      ...baseInput,
      experiences: [{ ...baseInput.experiences[0], end_date: "Dec 2023" }],
    }
    const result = buildLatex(input)
    expect(result).toContain("Jan 2022 -- Dec 2023")
  })

  it("escapes special characters in name", () => {
    const input = { ...baseInput, fullName: "O'Brien & Sons" }
    const result = buildLatex(input)
    expect(result).toContain("O'Brien \\& Sons")
  })

  it("includes project name and tech stack", () => {
    const result = buildLatex(baseInput)
    expect(result).toContain("Reed")
    expect(result).toContain("React, FastAPI")
  })

  it("includes skills sections", () => {
    const result = buildLatex(baseInput)
    expect(result).toContain("Python, TypeScript")
    expect(result).toContain("React, FastAPI")
    expect(result).toContain("Docker, Git")
  })

  it("includes GitHub link in project when github_url provided", () => {
    const result = buildLatex(baseInput)
    expect(result).toContain("https://github.com/user/reed")
  })

  it("omits GitHub link in project when github_url is null", () => {
    const input = {
      ...baseInput,
      projects: [{ ...baseInput.projects[0], github_url: null }],
    }
    const result = buildLatex(input)
    expect(result).not.toContain("\\textbar{}")
  })
})
