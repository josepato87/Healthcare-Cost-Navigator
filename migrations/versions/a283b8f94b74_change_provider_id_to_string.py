"""Change provider_id to String

Revision ID: a283b8f94b74
Revises: d678b183011f
Create Date: 2025-09-15 04:54:42.135036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a283b8f94b74'
down_revision: Union[str, None] = 'd678b183011f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop foreign key constraint on procedures.provider_id
    op.drop_constraint('procedures_provider_id_fkey', 'procedures', type_='foreignkey')
    # Alter provider_id in providers table to String
    op.alter_column('providers', 'provider_id',
        existing_type=sa.Integer(),
        type_=sa.String(),
        existing_nullable=True,
        postgresql_using="provider_id::varchar"
    )
    # Alter provider_id in procedures table to String
    op.alter_column('procedures', 'provider_id',
        existing_type=sa.Integer(),
        type_=sa.String(),
        existing_nullable=True,
        postgresql_using="provider_id::varchar"
    )
    # Recreate foreign key constraint on procedures.provider_id
    op.create_foreign_key(
        'procedures_provider_id_fkey',
        'procedures', 'providers',
        ['provider_id'], ['provider_id']
    )

def downgrade():
    op.drop_constraint('procedures_provider_id_fkey', 'procedures', type_='foreignkey')
    op.alter_column('providers', 'provider_id',
        existing_type=sa.String(),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="provider_id::integer"
    )
    op.alter_column('procedures', 'provider_id',
        existing_type=sa.String(),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="provider_id::integer"
    )
    op.create_foreign_key(
        'procedures_provider_id_fkey',
        'procedures', 'providers',
        ['provider_id'], ['provider_id']
    )

