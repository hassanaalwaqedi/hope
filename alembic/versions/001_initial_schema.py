"""Initial schema - users, sessions, consents, panic events

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

Creates the core HOPE database schema:
- users: User accounts with encrypted fields
- sessions: Therapy sessions with message history
- consents: Consent records with audit trail
- panic_events: Panic episode tracking
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('profile', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('consent_version', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    op.create_index('ix_users_deleted_at', 'users', ['deleted_at'])
    
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('state', sa.String(20), nullable=False, default='created'),
        sa.Column('messages', postgresql.JSONB(), nullable=False, default=[]),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('escalation_reason', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('ix_sessions_state', 'sessions', ['state'])
    op.create_index('ix_sessions_created_at', 'sessions', ['created_at'])
    
    # Create consents table
    op.create_table(
        'consents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('consent_type', sa.String(50), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('granted', sa.Boolean(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('granted_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('revocation_reason', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_consents_user_id', 'consents', ['user_id'])
    op.create_index('ix_consents_consent_type', 'consents', ['consent_type'])
    op.create_index('ix_consents_revoked_at', 'consents', ['revoked_at'])
    # Composite index for finding active consents
    op.create_index(
        'ix_consents_user_type_active',
        'consents',
        ['user_id', 'consent_type'],
        postgresql_where=sa.text('revoked_at IS NULL')
    )
    
    # Create panic_events table
    op.create_table(
        'panic_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('severity', sa.Integer(), nullable=False, default=0),
        sa.Column('urgency', sa.String(20), nullable=False, default='routine'),
        sa.Column('confidence_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('triggers', postgresql.ARRAY(sa.String(50)), nullable=False, default=[]),
        sa.Column('symptoms_reported', postgresql.ARRAY(sa.String(100)), nullable=False, default=[]),
        sa.Column('interventions_provided', postgresql.ARRAY(sa.String(50)), nullable=False, default=[]),
        sa.Column('interventions_used', postgresql.ARRAY(sa.String(50)), nullable=False, default=[]),
        sa.Column('resolution_time_seconds', sa.Integer(), nullable=True),
        sa.Column('user_feedback', sa.String(1000), nullable=True),
        sa.Column('feedback_rating', sa.Integer(), nullable=True),
        sa.Column('escalated', sa.Boolean(), nullable=False, default=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=False, default={}),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_panic_events_user_id', 'panic_events', ['user_id'])
    op.create_index('ix_panic_events_session_id', 'panic_events', ['session_id'])
    op.create_index('ix_panic_events_severity', 'panic_events', ['severity'])
    op.create_index('ix_panic_events_escalated', 'panic_events', ['escalated'])
    op.create_index('ix_panic_events_detected_at', 'panic_events', ['detected_at'])


def downgrade() -> None:
    op.drop_table('panic_events')
    op.drop_table('consents')
    op.drop_table('sessions')
    op.drop_table('users')
