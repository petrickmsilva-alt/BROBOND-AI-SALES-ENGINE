"""ORM models registered against the declarative base."""

from app.infrastructure.models.cliente_model import ClienteModel
from app.infrastructure.models.conversa_model import ConversaModel
from app.infrastructure.models.lead_model import LeadModel
from app.infrastructure.models.produto_model import ProdutoModel
from app.infrastructure.models.user_model import UserModel
from app.infrastructure.models.venda_model import VendaModel

__all__ = [
    "ClienteModel",
    "ConversaModel",
    "LeadModel",
    "ProdutoModel",
    "UserModel",
    "VendaModel",
]
