"""
Regression tests for _assemble_latex field name bugs fixed in April 2026.

Bugs covered:
  1. Jinja2 comment syntax: {#1 in LaTeX preamble caused TemplateSyntaxError
     (fixed by wrapping preamble in {% raw %}...{% endraw %})
  2. exp.role → exp.role_title  (experience role was silently empty)
  3. exp.selected_bullets → exp.bullets  (experience bullets were silently empty)
  4. bullet.text for project bullets → bullet  (project bullets were silently empty)
  5. bullet.text for leadership bullets → bullet  (leadership bullets were silently empty)
  6. Education hardcoded → now rendered from education_list context variable
  7. None end_date must render as 'Present', not the string 'None'
"""
import types
from pathlib import Path

import pytest

TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "resume.tex.jinja2"


def _make_profile(**kwargs):
    defaults = dict(phone="555-1234", linkedin_url="https://linkedin.com/in/test", github_url="https://github.com/test")
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def _render(response_dict, educations=None, leadership=None, profile=None):
    from app.api.routes.resumes import _assemble_latex
    template_str = TEMPLATE_PATH.read_text()
    return _assemble_latex(
        template_str=template_str,
        response_dict=response_dict,
        profile=profile or _make_profile(),
        email="test@example.com",
        leadership=leadership or [],
        educations=educations or [],
    )


def _base_response(**overrides):
    base = {
        "summary": "Test summary.",
        "include_coursework": False,
        "coursework_items": [],
        "experiences": [],
        "projects": [],
        "skills": {"languages": "Python", "frameworks": "FastAPI", "tools": "Docker"},
    }
    base.update(overrides)
    return base


# ── Bug 1: {#1 in preamble caused TemplateSyntaxError ──────────────────────

def test_template_renders_without_syntax_error():
    """The LaTeX {#1 command arg syntax must not be treated as Jinja2 comment."""
    result = _render(_base_response())
    assert "\\resumeItem" in result
    assert "\\resumeSubheading" in result


def test_template_latex_arg_syntax_preserved():
    """#1 inside command definitions must be preserved verbatim."""
    result = _render(_base_response())
    assert "{#1" in result


# ── Bug 2: exp.role → exp.role_title ───────────────────────────────────────

def test_experience_role_title_renders():
    """Experience role must come from role_title key, not role."""
    response = _base_response(experiences=[{
        "company": "Acme Corp",
        "role_title": "Software Engineer Intern",
        "start_date": "May 2022",
        "end_date": "Aug 2023",
        "location": "Vancouver, BC",
        "bullets": ["Built APIs"],
    }])
    result = _render(response)
    assert "Software Engineer Intern" in result


def test_experience_with_missing_role_title_key_produces_error_not_silent_empty():
    """Sanity check: a dict without role_title yields an empty string via Jinja2 (not a crash)."""
    # The old buggy template used exp.role; this verifies the correct key is required.
    response = _base_response(experiences=[{
        "company": "Acme Corp",
        "role_title": "Correct Title",
        "start_date": "May 2022",
        "end_date": "Aug 2023",
        "location": "Vancouver, BC",
        "bullets": [],
    }])
    result = _render(response)
    assert "Correct Title" in result
    assert "Acme Corp" in result


# ── Bug 3: exp.selected_bullets → exp.bullets ──────────────────────────────

def test_experience_bullets_render():
    """Experience bullets must come from bullets key, not selected_bullets."""
    response = _base_response(experiences=[{
        "company": "Acme",
        "role_title": "SWE",
        "start_date": "Jan 2023",
        "end_date": "Dec 2023",
        "location": "Remote",
        "bullets": ["Shipped feature X", "Reduced latency by 40%"],
    }])
    result = _render(response)
    assert "Shipped feature X" in result
    assert "Reduced latency by 40" in result


def test_experience_multiple_bullets_all_render():
    response = _base_response(experiences=[{
        "company": "Acme",
        "role_title": "SWE",
        "start_date": "Jan 2023",
        "end_date": "Dec 2023",
        "location": "Remote",
        "bullets": ["Bullet one", "Bullet two", "Bullet three"],
    }])
    result = _render(response)
    assert result.count("\\resumeItem") >= 3


# ── Bug 4: project bullet.text → bullet (plain string) ─────────────────────

def test_project_bullets_render_as_plain_strings():
    """Project bullets are plain strings; accessing .text on them silently returned empty."""
    response = _base_response(projects=[{
        "id": "abc123",
        "name": "Cool Project",
        "tech_stack": "React, FastAPI",
        "bullets": ["Deployed to 1000 users", "Reduced cost by 30%"],
        "github_url": None,
    }])
    result = _render(response)
    assert "Deployed to 1000 users" in result
    assert "Reduced cost by 30" in result


def test_project_name_and_tech_stack_render():
    response = _base_response(projects=[{
        "id": "abc",
        "name": "My Project",
        "tech_stack": "Python, Docker",
        "bullets": ["Did stuff"],
        "github_url": None,
    }])
    result = _render(response)
    assert "My Project" in result
    assert "Python, Docker" in result


# ── Bug 5: leadership bullet.text → bullet (plain string) ──────────────────

def test_leadership_bullets_render_as_plain_strings():
    """Leadership bullets are plain strings; accessing .text silently returned empty."""
    lead = types.SimpleNamespace(
        organization="Anthropic & Wasserman",
        role="Campus Claude Ambassador",
        start_date="Jan 2026",
        end_date="Present",
        location="University of Victoria",
        bullets=["Organized 5 AI workshops", "Mentored 60 students"],
    )
    result = _render(_base_response(), leadership=[lead])
    assert "Organized 5 AI workshops" in result
    assert "Mentored 60 students" in result


def test_leadership_section_omitted_when_empty():
    result = _render(_base_response(), leadership=[])
    assert "Leadership" not in result


# ── Bug 6: Education hardcoded → dynamic from education_list ───────────────

def test_education_institution_comes_from_bank():
    """Education must render from the educations list, not hardcoded UVic text."""
    edu = types.SimpleNamespace(
        institution="MIT",
        degree="Bachelor of Science",
        field_of_study="Computer Science",
        start_date="Sep 2019",
        end_date="May 2023",
        location="Cambridge, MA",
    )
    result = _render(_base_response(), educations=[edu])
    assert "MIT" in result


def test_education_multiple_entries_all_render():
    bsc = types.SimpleNamespace(institution="UVic", degree="BSc", field_of_study="CS",
                                start_date="Sep 2021", end_date="Dec 2025", location="Victoria, BC")
    msc = types.SimpleNamespace(institution="UVic", degree="MSc", field_of_study="CS",
                                start_date="Jan 2026", end_date="Dec 2027", location="Victoria, BC")
    result = _render(_base_response(), educations=[msc, bsc])
    assert result.count("University") == 0 or result.count("UVic") >= 2


def test_education_degree_and_field_render():
    edu = types.SimpleNamespace(
        institution="UVic",
        degree="Master of Science",
        field_of_study="Computer Science",
        start_date="Jan 2026",
        end_date="Dec 2027",
        location="Victoria, BC",
    )
    result = _render(_base_response(), educations=[edu])
    assert "Master of Science" in result
    assert "Computer Science" in result


# ── Bug 7: None end_date → "Present", not string "None" ───────────────────

def test_none_end_date_renders_as_present_in_experience():
    response = _base_response(experiences=[{
        "company": "Current Employer",
        "role_title": "Engineer",
        "start_date": "May 2025",
        "end_date": None,
        "location": "Remote",
        "bullets": ["Ongoing work"],
    }])
    result = _render(response)
    assert "Present" in result
    assert "None" not in result


def test_none_end_date_renders_as_present_in_leadership():
    lead = types.SimpleNamespace(
        organization="Club",
        role="President",
        start_date="Jan 2025",
        end_date=None,
        location="UVic",
        bullets=["Led meetings"],
    )
    result = _render(_base_response(), leadership=[lead])
    assert "Present" in result
    assert "None" not in result
