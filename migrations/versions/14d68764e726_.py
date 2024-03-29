"""empty message

Revision ID: 14d68764e726
Revises: d4a55ba8983b
Create Date: 2019-10-02 04:52:41.112256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14d68764e726'
down_revision = 'd4a55ba8983b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('state_id', sa.String(length=120), nullable=True))
    op.drop_column('artists', 'state')
    op.add_column('venues', sa.Column('state_id', sa.String(length=2), nullable=False))
    op.create_foreign_key(None, 'venues', 'choices', ['state_id'], ['id'])
    op.drop_column('venues', 'state')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venues', sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'venues', type_='foreignkey')
    op.drop_column('venues', 'state_id')
    op.add_column('artists', sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
    op.drop_column('artists', 'state_id')
    # ### end Alembic commands ###
