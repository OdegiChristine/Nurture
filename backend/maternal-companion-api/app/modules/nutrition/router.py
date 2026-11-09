from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import Principal, mother_only
from app.core.errors import NotFoundError
from app.modules.mothers.models import Mother
from app.modules.nutrition.service import nutrition_tip, trimester

router = APIRouter(prefix="/v1/mothers/me", tags=["nutrition"])


class NutritionOut(BaseModel):
    trimester: int
    tip: str


@router.get("/nutrition", response_model=NutritionOut)
async def my_nutrition(
    principal: Principal = mother_only, session: AsyncSession = Depends(get_session)
):
    mother = await session.get(Mother, principal.id)
    if mother is None:
        raise NotFoundError("Mother not found")
    weeks = mother.current_gestation_weeks()
    return NutritionOut(
        trimester=trimester(weeks), tip=nutrition_tip(weeks, mother.county, mother.language)
    )
