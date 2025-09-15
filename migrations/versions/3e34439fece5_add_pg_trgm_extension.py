"""Add pg_trgm extension

Revision ID: 3e34439fece5
Revises: a283b8f94b74
Create Date: 2025-09-15 06:51:48.391540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e34439fece5'
down_revision: Union[str, None] = 'a283b8f94b74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

def downgrade():
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")

