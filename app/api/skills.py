from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session, require_current_user
from app.models.skill import Skill
from app.models.user import User
from app.models.user_skill import UserSkill
from app.schemas.skill import (
    SkillCatalogEnvelope,
    SkillCatalogItem,
    UserSkillRead,
    UserSkillsEnvelope,
    UserSkillsUpsertEnvelope,
    UserSkillsUpsertRequest,
    UserSkillsUpsertResult,
)


router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/catalog", response_model=SkillCatalogEnvelope)
def get_skill_catalog(
    category: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db_session),
) -> SkillCatalogEnvelope:
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    if search:
        pattern = f"%{search}%"
        query = query.filter(Skill.name.ilike(pattern) | Skill.slug.ilike(pattern))

    skills = query.order_by(Skill.name.asc()).all()
    return SkillCatalogEnvelope(
        data=[SkillCatalogItem.model_validate(skill) for skill in skills]
    )


@router.get("/me", response_model=UserSkillsEnvelope)
def get_my_skills(
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> UserSkillsEnvelope:
    user_skills = db.query(UserSkill).filter(UserSkill.user_id == user.id).all()

    items = [
        UserSkillRead(
            skill_id=user_skill.skill.id,
            skill_slug=user_skill.skill.slug,
            skill_name=user_skill.skill.name,
            category=user_skill.skill.category,
            self_assessed_level=user_skill.self_assessed_level,
            measured_level=user_skill.measured_level,
            confidence_score=user_skill.confidence_score,
            evidence_count=user_skill.evidence_count,
            last_evaluated_at=user_skill.last_evaluated_at,
        )
        for user_skill in user_skills
    ]
    return UserSkillsEnvelope(data=items)


@router.put("/me", response_model=UserSkillsUpsertEnvelope)
def upsert_my_skills(
    payload: UserSkillsUpsertRequest,
    db: Session = Depends(get_db_session),
    user: User = Depends(require_current_user),
) -> UserSkillsUpsertEnvelope:
    updated_count = 0

    for item in payload.skills:
        user_skill = (
            db.query(UserSkill)
            .filter(UserSkill.user_id == user.id, UserSkill.skill_id == item.skill_id)
            .one_or_none()
        )

        if user_skill is None:
            user_skill = UserSkill(
                user_id=user.id,
                skill_id=item.skill_id,
                self_assessed_level=item.self_assessed_level,
            )
            db.add(user_skill)
        else:
            user_skill.self_assessed_level = item.self_assessed_level

        updated_count += 1

    db.commit()
    return UserSkillsUpsertEnvelope(data=UserSkillsUpsertResult(updated_count=updated_count))
