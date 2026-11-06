import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import audit
from app.core.errors import ConflictError
from app.core.security import encrypt_field, phone_hash
from app.modules.chp.service import assign_chp
from app.modules.mothers.models import Consent, Mother


async def get_mother_by_phone(session: AsyncSession, msisdn: str) -> Mother | None:
    result = await session.execute(select(Mother).where(Mother.phone_hash == phone_hash(msisdn)))
    return result.scalar_one_or_none()


async def create_mother(
    session: AsyncSession,
    *,
    msisdn: str,
    age: int,
    gestation_weeks: int,
    county: str,
    language: str = "en",
    pseudonym: str | None = None,
    dietary_preferences: list[str] | None = None,
    conditions: list[str] | None = None,
    consents: dict[str, bool] | None = None,
) -> Mother:
    mother = Mother(
        phone_hash=phone_hash(msisdn),
        phone_enc=encrypt_field(msisdn),
        pseudonym=pseudonym,
        age=age,
        gestation_weeks_at_enrolment=gestation_weeks,
        county=county,
        language=language,
        dietary_preferences=dietary_preferences or [],
        conditions=conditions or [],
        chp_id=await assign_chp(session, county),
    )
    session.add(mother)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise ConflictError("This phone number is already registered") from exc
    for scope, granted in (consents or {}).items():
        session.add(Consent(mother_id=mother.id, scope=scope, granted=granted))
    audit(
        session,
        actor_id=mother.id,
        actor_role="mother",
        action="mother_enrolled",
        resource_type="mother",
        resource_id=mother.id,
        detail={"has_chp": mother.chp_id is not None},
    )
    await session.commit()
    return mother


async def set_consent(
    session: AsyncSession, mother_id: uuid.UUID, scope: str, granted: bool
) -> None:
    result = await session.execute(
        select(Consent).where(Consent.mother_id == mother_id, Consent.scope == scope)
    )
    consent = result.scalar_one_or_none()
    if consent:
        consent.granted = granted
    else:
        session.add(Consent(mother_id=mother_id, scope=scope, granted=granted))
    audit(
        session,
        actor_id=mother_id,
        actor_role="mother",
        action="consent_granted" if granted else "consent_withdrawn",
        resource_type="consent",
        resource_id=mother_id,
        detail={"scope": scope},
    )
    await session.commit()


async def consented_mother_ids(
    session: AsyncSession, mother_ids: list[uuid.UUID], scope: str
) -> set[uuid.UUID]:
    if not mother_ids:
        return set()
    result = await session.execute(
        select(Consent.mother_id).where(
            Consent.mother_id.in_(mother_ids), Consent.scope == scope, Consent.granted.is_(True)
        )
    )
    return set(result.scalars())
