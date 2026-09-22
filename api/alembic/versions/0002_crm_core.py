"""CRM core: clientes, produtos, leads, conversas, vendas

Reshapes the placeholder ``leads`` table from PR001 into the full CRM schema:
customer-centric ``clientes`` with 1:N ``leads``, ``conversas`` and ``vendas``,
plus a standalone ``produtos`` catalogue.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-21
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.infrastructure.db.types import GUID

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # The PR001 leads table was a placeholder unrelated to the CRM model.
    op.drop_index("ix_leads_status", table_name="leads")
    op.drop_index("ix_leads_email", table_name="leads")
    op.drop_table("leads")

    op.create_table(
        "clientes",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("telefone", sa.String(length=32), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("instagram", sa.String(length=128), nullable=True),
        sa.Column("cidade", sa.String(length=128), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_clientes_nome", "clientes", ["nome"])
    op.create_index("ix_clientes_email", "clientes", ["email"])

    op.create_table(
        "produtos",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("categoria", sa.String(length=128), nullable=True),
        sa.Column("cor", sa.String(length=64), nullable=True),
        sa.Column("tamanho", sa.String(length=32), nullable=True),
        sa.Column("preco", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("estoque", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_produtos_sku", "produtos", ["sku"], unique=True)
    op.create_index("ix_produtos_categoria", "produtos", ["categoria"])

    op.create_table(
        "leads",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column(
            "cliente_id",
            GUID(),
            sa.ForeignKey("clientes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("origem", sa.String(length=64), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="novo"),
        sa.Column("interesse", sa.String(length=255), nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_leads_cliente_id", "leads", ["cliente_id"])
    op.create_index("ix_leads_status", "leads", ["status"])

    op.create_table(
        "conversas",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column(
            "cliente_id",
            GUID(),
            sa.ForeignKey("clientes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_conversas_cliente_id", "conversas", ["cliente_id"])

    op.create_table(
        "vendas",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column(
            "cliente_id",
            GUID(),
            sa.ForeignKey("clientes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("valor", sa.Numeric(precision=10, scale=2), nullable=False, server_default="0"),
        sa.Column("metodo_pagamento", sa.String(length=32), nullable=False, server_default="pix"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="pendente"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_vendas_cliente_id", "vendas", ["cliente_id"])
    op.create_index("ix_vendas_status", "vendas", ["status"])


def downgrade() -> None:
    op.drop_index("ix_vendas_status", table_name="vendas")
    op.drop_index("ix_vendas_cliente_id", table_name="vendas")
    op.drop_table("vendas")

    op.drop_index("ix_conversas_cliente_id", table_name="conversas")
    op.drop_table("conversas")

    op.drop_index("ix_leads_status", table_name="leads")
    op.drop_index("ix_leads_cliente_id", table_name="leads")
    op.drop_table("leads")

    op.drop_index("ix_produtos_categoria", table_name="produtos")
    op.drop_index("ix_produtos_sku", table_name="produtos")
    op.drop_table("produtos")

    op.drop_index("ix_clientes_email", table_name="clientes")
    op.drop_index("ix_clientes_nome", table_name="clientes")
    op.drop_table("clientes")

    # Recreate the PR001 placeholder leads table on downgrade.
    op.create_table(
        "leads",
        sa.Column("id", GUID(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="new"),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "owner_id",
            GUID(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_leads_email", "leads", ["email"])
    op.create_index("ix_leads_status", "leads", ["status"])
