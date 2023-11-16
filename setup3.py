from alembic import op
import sqlalchemy as sa

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