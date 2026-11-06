"""Import every model so Base.metadata (Alembic, tests) sees all tables."""

from app.core.audit import AuditLog  # noqa: F401
from app.modules.alerts.models import Alert  # noqa: F401
from app.modules.channels.models import InboundMessage  # noqa: F401
from app.modules.checkins.models import CheckIn  # noqa: F401
from app.modules.chp.models import Chp  # noqa: F401
from app.modules.mothers.models import Consent, Mother  # noqa: F401
