"""Fix provider_id type mismatch

Revision ID: e35028fc9827
Revises: 5f3bd912225b
Create Date: 2025-09-15 04:01:36.034441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e35028fc9827'
down_revision: Union[str, None] = '5f3bd912225b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop foreign key constraint on procedures.provider_id
    op.drop_constraint('procedures_provider_id_fkey', 'procedures', type_='foreignkey')
    # Alter provider_id in providers table to Integer
    op.alter_column('providers', 'provider_id',
        existing_type=sa.String(),
        type_=sa.Integer(),
        existing_nullable=True
    )
    # Alter provider_id in procedures table to Integer
    op.alter_column('procedures', 'provider_id',
        existing_type=sa.String(),
        type_=sa.Integer(),
        existing_nullable=True
    )
    # Recreate foreign key constraint on procedures.provider_id
    op.create_foreign_key(
        'procedures_provider_id_fkey',
        'procedures', 'providers',
        ['provider_id'], ['provider_id']
    )


def downgrade() -> None:
    # Drop foreign key constraint on procedures.provider_id
    op.drop_constraint('procedures_provider_id_fkey', 'procedures', type_='foreignkey')
    # Alter provider_id in providers table to String
    op.alter_column('providers', 'provider_id',
        existing_type=sa.Integer(),
        type_=sa.String(),
        existing_nullable=True
    )
    # Alter provider_id in procedures table to String
    op.alter_column('procedures', 'provider_id',
        existing_type=sa.Integer(),
        type_=sa.String(),
        existing_nullable=True
    )
    # Recreate foreign key constraint on procedures.provider_id
    op.create_foreign_key(
        'procedures_provider_id_fkey',
        'procedures', 'providers',
        ['provider_id'], ['provider_id']
    )
