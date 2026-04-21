from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.models.skill import Skill
from app.schemas.skill import SkillCatalogEnvelope, SkillCatalogItem


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
