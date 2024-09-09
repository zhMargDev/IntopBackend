"""add new tables

Revision ID: 69e37988dff8
Revises: 3ad2602acc14
Create Date: 2024-09-08 18:16:48.604828

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69e37988dff8'
down_revision: Union[str, None] = '3ad2602acc14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('advertisements', sa.Column('service', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'advertisements', 'services', ['service'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'advertisements', type_='foreignkey')
    op.drop_column('advertisements', 'service')
    # ### end Alembic commands ###
