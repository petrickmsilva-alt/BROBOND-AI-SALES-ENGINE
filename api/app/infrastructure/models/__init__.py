"""ORM models registered against the declarative base."""

from app.infrastructure.models.lead_model import LeadModel
from app.infrastructure.models.user_model import UserModel

__all__ = ["LeadModel", "UserModel"]
