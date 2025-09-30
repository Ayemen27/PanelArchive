"""Initial baseline migration - Documents existing schema

Revision ID: 001_initial_baseline
Revises: 
Create Date: 2025-09-30 23:00:00.000000

This migration serves as the baseline for the existing database schema.
It does not modify the database structure, but documents what exists.

Current schema includes:
- backup: Backup management table
- binding: Domain binding records
- config: System configuration
- crontab: Scheduled tasks
- databases: Database management
- firewall: Firewall rules
- ftps: FTP accounts
- logs: System logs
- sites: Website management
- domain: Domain records
- users: User accounts
- tasks: Task queue
- And 15 other tables for various features
"""
from alembic import op
import sqlalchemy as sa

revision = '001_initial_baseline'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    This migration does not change the database structure.
    It serves as a baseline/checkpoint for the existing schema.
    """
    pass


def downgrade() -> None:
    """
    Cannot downgrade from baseline.
    """
    pass
