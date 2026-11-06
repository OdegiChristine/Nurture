import uuid
from dataclasses import dataclass
from enum import StrEnum

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.security import decode_access_token

_bearer = HTTPBearer(auto_error=False)


class Role(StrEnum):
    MOTHER = "mother"
    CHP = "chp"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


@dataclass(frozen=True)
class Principal:
    id: uuid.UUID
    role: Role


async def get_principal(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> Principal:
    if creds is None:
        raise UnauthorizedError("Missing bearer token")
    try:
        claims = decode_access_token(creds.credentials)
        return Principal(id=uuid.UUID(claims["sub"]), role=Role(claims["role"]))
    except (jwt.PyJWTError, ValueError) as exc:
        raise UnauthorizedError("Invalid or expired token") from exc


def require_role(*roles: Role):
    async def _dep(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.role not in roles:
            raise ForbiddenError("Insufficient role")
        return principal

    return _dep


# Module-level singletons keep route signatures short (and satisfy lint rule B008).
mother_only = Depends(require_role(Role.MOTHER))
chp_only = Depends(require_role(Role.CHP))
