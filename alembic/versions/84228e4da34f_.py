"""empty message

Revision ID: 84228e4da34f
Revises: a0c8c695ab19
Create Date: 2025-03-31 10:06:00.160309

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '84228e4da34f'
down_revision: Union[str, None] = 'a0c8c695ab19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_teams_name', table_name='teams')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_teams_name', 'teams', ['name'], unique=True)
    # ### end Alembic commands ###
