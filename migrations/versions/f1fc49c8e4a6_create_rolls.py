"""Create_Rolls

Revision ID: f1fc49c8e4a6
Revises: 
Create Date: 2025-03-11 18:46:58.920610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1fc49c8e4a6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rolls',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('length', sa.Integer(), nullable=False),
    sa.Column('weight', sa.Integer(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('create_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
    sa.Column('update_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
    sa.Column('delete_at', sa.Date(), nullable=True),
    sa.CheckConstraint('length > 0', name='check_length_positive'),
    sa.CheckConstraint('weight > 0', name='check_weight_positive'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rolls_create_at'), 'rolls', ['create_at'], unique=False)
    op.create_index(op.f('ix_rolls_delete_at'), 'rolls', ['delete_at'], unique=False)
    op.create_index(op.f('ix_rolls_is_deleted'), 'rolls', ['is_deleted'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_rolls_is_deleted'), table_name='rolls')
    op.drop_index(op.f('ix_rolls_delete_at'), table_name='rolls')
    op.drop_index(op.f('ix_rolls_create_at'), table_name='rolls')
    op.drop_table('rolls')
    # ### end Alembic commands ###
