"""make user_id and trash_category_id nullable in disposal_histories

Revision ID: ba608d2a1e41
Revises: 0f139a9d3438
Create Date: 2026-04-06 07:40:27.330158

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba608d2a1e41'
down_revision: Union[str, Sequence[str], None] = '0f139a9d3438'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('disposal_histories', schema=None) as batch_op:
        batch_op.alter_column('trash_category_id',
                   existing_type=sa.INTEGER(),
                   nullable=True)
        batch_op.alter_column('user_id',
                   existing_type=sa.INTEGER(),
                   nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('disposal_histories', schema=None) as batch_op:
        batch_op.alter_column('user_id',
                   existing_type=sa.INTEGER(),
                   nullable=False)
        batch_op.alter_column('trash_category_id',
                   existing_type=sa.INTEGER(),
                   nullable=False)
    # ### end Alembic commands ###
