"""Add current_version_id to tracks

Revision ID: 6e69d94d8db6
Revises: 
Create Date: 2023-11-16 02:04:32.021608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e69d94d8db6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ...

def upgrade():
    # Start batch mode
    with op.batch_alter_table('tracks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('current_version_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(batch_op.f('fk_tracks_current_version_id_versions'), 'versions', ['current_version_id'], ['id'])

def downgrade():
    with op.batch_alter_table('tracks', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_tracks_current_version_id_versions'), type_='foreignkey')
        batch_op.drop_column('current_version_id')