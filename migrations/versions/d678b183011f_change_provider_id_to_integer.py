"""Change provider_id to integer

Revision ID: d678b183011f
Revises: e35028fc9827
Create Date: 2025-09-15 04:29:48.218449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd678b183011f'
down_revision: Union[str, None] = 'e35028fc9827'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint('procedures_provider_id_fkey', 'procedures', type_='foreignkey')
    op.alter_column('providers', 'provider_id',
        existing_type=sa.VARCHAR(),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="provider_id::integer"
    )
    op.alter_column('procedures', 'provider_id',
        existing_type=sa.VARCHAR(),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="provider_id::integer"
    )
    op.create_foreign_key(
        'procedures_provider_id_fkey',
        'procedures', 'providers',
        ['provider_id'], ['provider_id']
    )

def downgrade():
    op.drop_constraint('procedures_provider_id_fkey', 'procedures', type_='foreignkey')
    op.alter_column('providers', 'provider_id',
        existing_type=sa.Integer(),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using="provider_id::varchar"
    )
    op.alter_column('procedures', 'provider_id',
        existing_type=sa.Integer(),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using="provider_id::varchar"
    )
    op.create_foreign_key(
        'procedures_provider_id_fkey',
        'procedures', 'providers',
        ['provider_id'], ['provider_id']
    )
