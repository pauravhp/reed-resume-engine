import uuid
from datetime import datetime

from app.models import (
    Application,
    Education,
    Experience,
    JobPosting,
    Leadership,
    Profile,
    Project,
    Skills,
)


def test_profile_defaults():
    p = Profile(user_id=uuid.uuid4())
    assert p.bio_context is None
    assert p.groq_api_key is None
    assert p.phone is None
    assert p.linkedin_url is None
    assert p.github_url is None


def test_project_defaults():
    p = Project(user_id=uuid.uuid4(), name="Test Project")
    assert p.bullets == []
    assert p.display_order == 0
    assert p.github_url is None
    assert isinstance(p.id, uuid.UUID)


def test_experience_defaults():
    e = Experience(
        user_id=uuid.uuid4(),
        company="Acme",
        role="Engineer",
        start_date="Jan 2024",
        end_date="Present",
    )
    assert e.bullets == []
    assert e.display_order == 0


def test_skills_defaults():
    s = Skills(user_id=uuid.uuid4())
    assert s.languages == []
    assert s.frameworks == []
    assert s.tools == []


def test_education_defaults():
    ed = Education(
        user_id=uuid.uuid4(),
        institution="University of Victoria",
        degree="Bachelor of Science",
        field_of_study="Computer Science",
        start_date="Sep 2021",
        end_date="Dec 2025",
        location="Victoria, BC",
    )
    assert ed.gpa is None
    assert ed.coursework == []


def test_leadership_defaults():
    l = Leadership(
        user_id=uuid.uuid4(),
        organization="UVic Engineering Club",
        role="VP Events",
        start_date="Sep 2024",
        end_date="Present",
    )
    assert l.bullets == []
    assert l.display_order == 0


def test_job_posting_defaults():
    jp = JobPosting(url="https://example.com/job/123", jd_text="We are hiring...")
    assert jp.company is None
    assert isinstance(jp.scraped_at, datetime)


def test_application_defaults():
    app = Application(
        user_id=uuid.uuid4(),
        generated_latex="\\documentclass{article}",
    )
    assert app.status == "not_applied"
    assert app.generated_json == {}
    assert app.notes is None
    assert isinstance(app.created_at, datetime)
