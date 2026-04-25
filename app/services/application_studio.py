from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from app.models.cv import CvFeedback, CvVersion, CvVersionStatus
from app.models.job import Job, JobGapAnalysis, JobParse, UserJob
from app.models.skill import Skill
from app.models.user_profile import UserProfile
from app.models.user_skill import UserSkill


KNOWN_SKILLS = [
    "python",
    "typescript",
    "javascript",
    "fastapi",
    "postgresql",
    "sql",
    "react",
    "next.js",
    "docker",
    "kubernetes",
    "aws",
    "gcp",
    "azure",
    "distributed systems",
    "system design",
    "data platform",
    "machine learning",
    "llm",
    "testing",
    "ci/cd",
]


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        normalized = item.strip()
        key = normalized.lower()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


def _extract_bullets(raw_description: str, markers: tuple[str, ...]) -> list[str]:
    lines = [line.strip(" -•\t") for line in raw_description.splitlines()]
    selected: list[str] = []
    capture = False
    for line in lines:
        lower = line.lower()
        if any(marker in lower for marker in markers):
            capture = True
            continue
        if capture and any(marker in lower for marker in ("requirements", "qualifications", "nice to have", "benefits")):
            break
        if capture and len(line) > 12:
            selected.append(line)
    return selected[:6]


def parse_job_description(job: Job) -> JobParse:
    lower = job.raw_description.lower()
    required_skills = _unique([skill for skill in KNOWN_SKILLS if skill in lower])
    preferred_skills = _unique(
        [skill for skill in required_skills if re.search(rf"(nice|preferred|bonus).{{0,80}}{re.escape(skill)}", lower)]
    )
    keywords = _unique(required_skills + re.findall(r"\b(?:platform|scalability|backend|ai|data|cloud|automation)\b", lower))
    responsibilities = _extract_bullets(job.raw_description, ("responsibilities", "what you will do", "you will"))
    if not responsibilities:
        responsibilities = [sentence.strip() for sentence in re.split(r"[.!?]", job.raw_description) if len(sentence.strip()) > 40][:4]

    seniority = job.seniority
    if seniority is None:
        if any(term in lower for term in ("senior", "staff", "principal", "lead")):
            seniority = "senior"
        elif any(term in lower for term in ("junior", "graduate", "entry")):
            seniority = "junior"
        else:
            seniority = "mid"

    return JobParse(
        job_id=job.id,
        parsed_title=job.title,
        parsed_company_name=job.company_name,
        responsibilities_json=responsibilities,
        required_skills_json=required_skills,
        preferred_skills_json=preferred_skills,
        keywords_json=keywords,
        seniority_assessment=seniority,
        summary_markdown=f"This role emphasizes {', '.join(keywords[:4]) or 'software engineering execution'}.",
        prompt_version="epic4-v1",
        model_name="deterministic-parser",
    )


def collect_profile_skill_names(profile: UserProfile | None, user_skills: list[UserSkill]) -> set[str]:
    names = {item.skill.name.lower() for item in user_skills if isinstance(getattr(item, "skill", None), Skill)}
    if profile and profile.stack:
        names.update(item.lower() for item in profile.stack)
    return names


def latest_parse_for(job: Job) -> JobParse | None:
    if not job.parses:
        return None
    return sorted(job.parses, key=lambda item: item.created_at, reverse=True)[0]


def analyze_job_gap(
    user_job: UserJob,
    profile: UserProfile | None,
    user_skills: list[UserSkill],
    cv_versions: list[CvVersion],
) -> JobGapAnalysis:
    job_parse = latest_parse_for(user_job.job)
    required_skills = job_parse.required_skills_json if job_parse else []
    profile_skills = collect_profile_skill_names(profile, user_skills)
    cv_text = "\n".join(str(version.structured_content_json).lower() for version in cv_versions)

    matched = [{"skill": skill, "strength": "strong"} for skill in required_skills if skill.lower() in profile_skills or skill.lower() in cv_text]
    missing = [{"skill": skill, "severity": "medium"} for skill in required_skills if skill.lower() not in profile_skills and skill.lower() not in cv_text]
    weak = [{"skill": skill, "issue": "Present in profile, but weak evidence in CV"} for skill in required_skills if skill.lower() in profile_skills and skill.lower() not in cv_text]
    match_score = round((len(matched) / max(1, len(required_skills))) * 10, 2)
    user_job.match_score = match_score

    return JobGapAnalysis(
        user_job_id=user_job.id,
        fit_summary_markdown=f"You currently match {len(matched)} of {len(required_skills)} extracted required skills.",
        matched_skills_json=matched,
        missing_skills_json=missing,
        weak_evidence_json=weak,
        recommendation_json={
            "applyNow": match_score >= 6,
            "priority": "high" if match_score >= 7 else "medium",
            "nextActions": [
                "Tailor CV toward the strongest matching requirements",
                "Add concrete evidence for missing or weak skills",
            ],
        },
        prompt_version="epic4-v1",
        model_name="deterministic-gap-analyzer",
    )


def render_cv_markdown(content: dict[str, Any]) -> str:
    header = content.get("header", {})
    lines = [str(header.get("fullName") or "Candidate")]
    if header.get("email") or header.get("location"):
        lines.append(" | ".join(str(item) for item in [header.get("email"), header.get("location")] if item))
    if content.get("summary"):
        lines.extend(["", "## Summary", str(content["summary"])])
    if content.get("skills"):
        lines.extend(["", "## Skills", str(content["skills"])])
    if content.get("experience"):
        lines.append("")
        lines.append("## Experience")
        for item in content["experience"]:
            lines.append(f"### {item.get('role', 'Role')} - {item.get('company', 'Company')}")
            for bullet in item.get("bullets", []):
                lines.append(f"- {bullet}")
    return "\n".join(lines)


def tailor_cv(base_version: CvVersion, job: Job, job_parse: JobParse | None, preferences: dict[str, Any]) -> CvVersion:
    content = deepcopy(base_version.structured_content_json)
    keywords = (job_parse.keywords_json if job_parse else [])[:6]
    required_skills = job_parse.required_skills_json if job_parse else []
    emphasis = preferences.get("emphasize") or []
    content["summary"] = (
        f"{content.get('summary') or 'Software engineer'} Targeted for {job.title}"
        f" with emphasis on {', '.join(_unique(keywords + emphasis)[:6]) or 'relevant delivery'}."
    )
    for experience in content.get("experience", []):
        bullets = experience.get("bullets", [])
        experience["bullets"] = [
            f"{bullet} Relevant keywords: {', '.join(_unique(required_skills)[:3])}."
            for bullet in bullets
        ]

    return CvVersion(
        cv_document_id=base_version.cv_document_id,
        based_on_version_id=base_version.id,
        job_id=job.id,
        status=CvVersionStatus.tailored,
        title=f"Tailored CV - {job.title}",
        summary=content.get("summary"),
        structured_content_json=content,
        rendered_markdown=render_cv_markdown(content),
        ats_plain_text=render_cv_markdown(content),
        created_by_ai=True,
        prompt_version="epic4-v1",
        model_name="deterministic-cv-tailor",
    )


def generate_cv_feedback(version: CvVersion) -> CvFeedback:
    content_text = str(version.structured_content_json).lower()
    has_metrics = bool(re.search(r"\d+%|\b\d+x\b|\b\d+\s*(users|requests|ms|seconds|minutes)\b", content_text))
    generic_count = sum(content_text.count(term) for term in ("responsible for", "worked on", "helped with"))
    score = 8.0
    if not has_metrics:
        score -= 1.0
    if generic_count:
        score -= min(2.0, generic_count * 0.5)

    weaknesses = []
    suggestions = []
    if not has_metrics:
        weaknesses.append("Some bullets lack measurable impact.")
        suggestions.append("Add metrics such as latency, throughput, adoption, or reliability improvement.")
    if generic_count:
        weaknesses.append("Some wording is generic.")
        suggestions.append("Replace passive phrasing with action, scope, and outcome.")

    return CvFeedback(
        cv_version_id=version.id,
        score=round(score, 2),
        strengths_json=["Structured CV content is available", "Keyword alignment can be evaluated"],
        weaknesses_json=weaknesses or ["No major deterministic issues found"],
        suggestions_json=suggestions or ["Keep tailoring bullets toward job evidence"],
        prompt_version="epic4-v1",
        model_name="deterministic-cv-feedback",
    )
