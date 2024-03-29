"""empty message

Revision ID: 00e3fd940dd2
Revises: 013945d1005d
Create Date: 2019-09-30 09:38:56.739556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '00e3fd940dd2'
down_revision = '013945d1005d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('venue_genres',
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venues.id'], ),
    sa.PrimaryKeyConstraint('venue_id', 'genre_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('venue_genres')
    # ### end Alembic commands ###
