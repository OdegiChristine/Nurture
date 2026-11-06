import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.deps import Principal, Role, mother_only
from app.core.errors import AppError, NotFoundError
from app.core.security import create_access_token, normalize_msisdn
from app.modules.mothers import service
from app.modules.mothers.models import Mother
from app.modules.mothers.schemas import ConsentUpdate, MotherCreate, MotherOut, OnboardedOut

router = APIRouter(prefix="/v1/mothers", tags=["mothers"])


def to_out(mother: Mother) -> MotherOut:
    return MotherOut(
        id=mother.id,
        pseudonym=mother.pseudonym,
        age=mother.age,
        gestation_weeks=mother.current_gestation_weeks(),
        county=mother.county,
        language=mother.language,
        has_chp=mother.chp_id is not None,
    )


@router.post("", response_model=OnboardedOut, status_code=201)
async def onboard(body: MotherCreate, session: AsyncSession = Depends(get_session)):
    # TODO(security): verify phone ownership with an OTP before issuing a token, and rate-limit.
    try:
        msisdn = normalize_msisdn(body.phone)
    except ValueError as exc:
        raise AppError(str(exc)) from exc
    mother = await service.create_mother(
        session,
        msisdn=msisdn,
        age=body.age,
        gestation_weeks=body.gestation_weeks,
        county=body.county,
        language=body.language,
        pseudonym=body.pseudonym,
        dietary_preferences=body.dietary_preferences,
        conditions=body.conditions,
        consents={"chp_contact": body.consent_chp_contact},
    )
    return OnboardedOut(
        mother=to_out(mother), access_token=create_access_token(str(mother.id), Role.MOTHER)
    )


@router.get("/me", response_model=MotherOut)
async def me(
    principal: Principal = mother_only,
    session: AsyncSession = Depends(get_session),
):
    mother = await session.get(Mother, principal.id)
    if mother is None:
        raise NotFoundError("Mother not found")
    return to_out(mother)


@router.put("/me/consents", status_code=204)
async def update_consent(
    body: ConsentUpdate,
    principal: Principal = mother_only,
    session: AsyncSession = Depends(get_session),
):
    await service.set_consent(session, uuid.UUID(str(principal.id)), body.scope, body.granted)
