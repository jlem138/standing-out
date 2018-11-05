"""empty message

Revision ID: 4df5be7b188d
Revises: 
Create Date: 2018-11-05 03:37:19.232599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4df5be7b188d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('leagues',
    sa.Column('league_name', sa.String(length=200), nullable=False),
    sa.Column('number_of_games', sa.Integer(), nullable=True),
    sa.Column('number_of_conferences', sa.Integer(), nullable=True),
    sa.Column('number_of_total_teams', sa.Integer(), nullable=True),
    sa.Column('number_of_rounds', sa.Integer(), nullable=True),
    sa.Column('number_of_qualifiers', sa.Integer(), nullable=True),
    sa.Column('is_byes', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('league_name')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=60), nullable=True),
    sa.Column('username', sa.String(length=60), nullable=True),
    sa.Column('first_name', sa.String(length=60), nullable=True),
    sa.Column('last_name', sa.String(length=60), nullable=True),
    sa.Column('phone_number', sa.String(length=10), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_first_name'), 'users', ['first_name'], unique=False)
    op.create_index(op.f('ix_users_last_name'), 'users', ['last_name'], unique=False)
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('teams',
    sa.Column('name', sa.String(length=60), nullable=False),
    sa.Column('division_name', sa.String(length=60), nullable=True),
    sa.Column('conference_name', sa.String(length=60), nullable=True),
    sa.Column('league_name', sa.String(length=60), nullable=False),
    sa.Column('wins', sa.Integer(), nullable=True),
    sa.Column('losses', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['league_name'], ['leagues.league_name'], ),
    sa.PrimaryKeyConstraint('name')
    )
    op.create_table('updates',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=60), nullable=False),
    sa.Column('first_name', sa.String(length=60), nullable=True),
    sa.Column('last_name', sa.String(length=60), nullable=True),
    sa.Column('league_name', sa.String(length=60), nullable=False),
    sa.Column('phone_number', sa.String(length=10), nullable=True),
    sa.Column('is_admin', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['league_name'], ['leagues.league_name'], ),
    sa.ForeignKeyConstraint(['username'], ['users.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_updates_first_name'), 'updates', ['first_name'], unique=False)
    op.create_index(op.f('ix_updates_last_name'), 'updates', ['last_name'], unique=False)
    op.create_index(op.f('ix_updates_phone_number'), 'updates', ['phone_number'], unique=True)
    op.create_table('events',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('day', sa.Date(), nullable=True),
    sa.Column('winner', sa.String(length=200), nullable=False),
    sa.Column('loser', sa.String(length=200), nullable=False),
    sa.Column('league_name', sa.String(length=60), nullable=False),
    sa.Column('winning_score', sa.Integer(), nullable=True),
    sa.Column('losing_score', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['league_name'], ['leagues.league_name'], ),
    sa.ForeignKeyConstraint(['loser'], ['teams.name'], ),
    sa.ForeignKeyConstraint(['winner'], ['teams.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rankings',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('team', sa.String(length=200), nullable=False),
    sa.Column('wins', sa.Integer(), nullable=True),
    sa.Column('losses', sa.Integer(), nullable=True),
    sa.Column('games_played', sa.Integer(), nullable=True),
    sa.Column('gb', sa.Integer(), nullable=True),
    sa.Column('mnumber', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['team'], ['teams.name'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rankings')
    op.drop_table('events')
    op.drop_index(op.f('ix_updates_phone_number'), table_name='updates')
    op.drop_index(op.f('ix_updates_last_name'), table_name='updates')
    op.drop_index(op.f('ix_updates_first_name'), table_name='updates')
    op.drop_table('updates')
    op.drop_table('teams')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_index(op.f('ix_users_last_name'), table_name='users')
    op.drop_index(op.f('ix_users_first_name'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('leagues')
    # ### end Alembic commands ###