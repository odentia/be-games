"""Create games tables

Revision ID: 001
Revises: 
Create Date: 2024-11-20 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'games',
        sa.Column('id', sa.String(length=64), primary_key=True),
        sa.Column('rawg_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('slug', sa.String(length=255), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metacritic', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('release_date', sa.Date(), nullable=True),
        sa.Column('developer', sa.String(length=255), nullable=True),
        sa.Column('publisher', sa.String(length=255), nullable=True),
        sa.Column('background_image', sa.String(length=512), nullable=True),
        sa.Column('website', sa.String(length=512), nullable=True),
        sa.Column('playtime', sa.Integer(), nullable=True),
        sa.Column('age_rating', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'game_platforms',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('game_id', sa.String(length=64), sa.ForeignKey('games.id', ondelete='CASCADE')),
        sa.Column('name', sa.String(length=128), nullable=False),
    )

    op.create_table(
        'game_genres',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('game_id', sa.String(length=64), sa.ForeignKey('games.id', ondelete='CASCADE')),
        sa.Column('name', sa.String(length=128), nullable=False),
    )

    op.create_table(
        'game_tags',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('game_id', sa.String(length=64), sa.ForeignKey('games.id', ondelete='CASCADE')),
        sa.Column('name', sa.String(length=128), nullable=False),
    )

    op.create_table(
        'game_screenshots',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('game_id', sa.String(length=64), sa.ForeignKey('games.id', ondelete='CASCADE')),
        sa.Column('url', sa.String(length=512), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('game_screenshots')
    op.drop_table('game_tags')
    op.drop_table('game_genres')
    op.drop_table('game_platforms')
    op.drop_table('games')
