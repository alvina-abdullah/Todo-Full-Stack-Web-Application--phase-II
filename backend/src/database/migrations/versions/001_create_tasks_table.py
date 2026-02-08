"""Create tasks table

Revision ID: 001
Revises:
Create Date: 2026-02-08

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create tasks table with indexes."""
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on user_id for efficient user-filtered queries
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])

    # Create composite index on (user_id, created_at) for sorted user task lists
    op.create_index('ix_tasks_user_created', 'tasks', ['user_id', 'created_at'])


def downgrade() -> None:
    """Drop tasks table and indexes."""
    op.drop_index('ix_tasks_user_created', table_name='tasks')
    op.drop_index('ix_tasks_user_id', table_name='tasks')
    op.drop_table('tasks')
