"""initial_schema_and_models

Revision ID: e75c1c186642
Revises: 
Create Date: 2026-09-05 17:34:14.505499

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e75c1c186642'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('username', sa.String(), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), server_default='coordinator'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    # 2. specialists
    op.create_table(
        'specialists',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('specialization', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('availability_status', sa.String(), server_default='AVAILABLE', nullable=False),
        sa.Column('next_available_date', sa.DateTime(), nullable=True),
        sa.Column('active', sa.Boolean(), server_default='1', nullable=False),
    )

    # 3. cases
    op.create_table(
        'cases',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('child_identifier', sa.String(), nullable=False),
        sa.Column('referral_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default='NEW', nullable=False),
        sa.Column('coordinator_id', sa.String(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('assigned_specialist_id', sa.String(), sa.ForeignKey('specialists.id'), nullable=True),
        sa.Column('current_bottleneck', sa.String(), nullable=True),
        sa.Column('current_responsible_person', sa.String(), nullable=True),
        sa.Column('coordinator_notes', sa.Text(), nullable=True),
        sa.Column('diagnostic_details', sa.Text(), nullable=True),
        sa.Column('educator_summary', sa.Text(), nullable=True),
        sa.Column('created_date', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('last_activity', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('next_followup_date', sa.DateTime(), nullable=True),
        sa.Column('followup_attempts', sa.Integer(), server_default='0', nullable=False),
    )

    # 4. case_events
    op.create_table(
        'case_events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # 5. documents
    op.create_table(
        'documents',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('document_name', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default='PENDING', nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
    )

    # 6. communications
    op.create_table(
        'communications',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('recipient_type', sa.String(), nullable=False),
        sa.Column('recipient_id', sa.String(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), server_default='SENT', nullable=False),
        sa.Column('sent_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('response_received', sa.Boolean(), server_default='0', nullable=False),
    )

    # 7. appointments
    op.create_table(
        'appointments',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('specialist_id', sa.String(), sa.ForeignKey('specialists.id'), nullable=True),
        sa.Column('scheduled_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), server_default='REQUESTED', nullable=False),
    )

    # 8. escalations
    op.create_table(
        'escalations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(), server_default='HIGH', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # 9. follow_ups
    op.create_table(
        'follow_ups',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('scheduled_for', sa.DateTime(), nullable=False),
        sa.Column('completed', sa.Boolean(), server_default='0', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
    )

    # 10. agent_runs
    op.create_table(
        'agent_runs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('thread_id', sa.String(), unique=True, nullable=False),
        sa.Column('status', sa.String(), server_default='RUNNING', nullable=False),
        sa.Column('started_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )

    # 11. agent_run_steps
    op.create_table(
        'agent_run_steps',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('run_id', sa.String(), sa.ForeignKey('agent_runs.id'), nullable=False),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('node_name', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default='COMPLETED', nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # 12. agent_observations
    op.create_table(
        'agent_observations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('run_id', sa.String(), sa.ForeignKey('agent_runs.id'), nullable=True),
        sa.Column('observed_status', sa.String(), nullable=True),
        sa.Column('observed_bottleneck', sa.String(), nullable=True),
        sa.Column('timeline_snapshot', sa.Text(), nullable=True),
        sa.Column('observed_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # 13. bottlenecks
    op.create_table(
        'bottlenecks',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('run_id', sa.String(), sa.ForeignKey('agent_runs.id'), nullable=True),
        sa.Column('bottleneck_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # 14. agent_recommendations
    op.create_table(
        'agent_recommendations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('run_id', sa.String(), sa.ForeignKey('agent_runs.id'), nullable=True),
        sa.Column('bottleneck', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('recommended_action', sa.String(), nullable=False),
        sa.Column('priority', sa.String(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('evidence', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), server_default='PENDING', nullable=False),
        sa.Column('human_modified_action', sa.String(), nullable=True),
        sa.Column('approval_timestamp', sa.DateTime(), nullable=True),
        sa.Column('approver_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # 15. actions
    op.create_table(
        'actions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('recommendation_id', sa.String(), sa.ForeignKey('agent_recommendations.id'), nullable=True),
        sa.Column('action_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default='EXECUTED', nullable=False),
        sa.Column('result_message', sa.Text(), nullable=True),
        sa.Column('entity_id', sa.String(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    # 16. action_verifications
    op.create_table(
        'action_verifications',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('action_id', sa.String(), sa.ForeignKey('actions.id'), nullable=False),
        sa.Column('case_id', sa.String(), sa.ForeignKey('cases.id'), nullable=False),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('verification_status', sa.String(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('verified_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('action_verifications')
    op.drop_table('actions')
    op.drop_table('agent_recommendations')
    op.drop_table('bottlenecks')
    op.drop_table('agent_observations')
    op.drop_table('agent_run_steps')
    op.drop_table('agent_runs')
    op.drop_table('follow_ups')
    op.drop_table('escalations')
    op.drop_table('appointments')
    op.drop_table('communications')
    op.drop_table('documents')
    op.drop_table('case_events')
    op.drop_table('cases')
    op.drop_table('specialists')
    op.drop_table('users')
