"""language_capability_and_voice_m2m

Revision ID: 2f8a1c9e4b10
Revises: 17595624f06f
Create Date: 2026-09-17 19:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f8a1c9e4b10'
down_revision: Union[str, Sequence[str], None] = '17595624f06f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to include language metadata, provider capabilities, and voice M2M."""
    # 1. Update languages table
    op.add_column(
        'languages',
        sa.Column('direction', sa.String(length=5), nullable=False, server_default='ltr')
    )
    op.add_column(
        'languages',
        sa.Column('metadata', sa.JSON(), nullable=True)
    )
    op.add_column(
        'languages',
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True)
    )

    # 2. Update voices table
    op.add_column(
        'voices',
        sa.Column('provider_voice_id', sa.String(length=100), nullable=True)
    )
    op.add_column(
        'voices',
        sa.Column('metadata', sa.JSON(), nullable=True)
    )
    op.create_index(op.f('ix_voices_provider_voice_id'), 'voices', ['provider_voice_id'], unique=False)

    # 3. Create provider_capabilities table
    op.create_table(
        'provider_capabilities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('language_code', sa.String(length=10), nullable=False),
        sa.Column('provider_language_code', sa.String(length=50), nullable=True),
        sa.Column('supported', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['language_code'], ['languages.code'], name=op.f('fk_provider_capabilities_language_code_languages'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_provider_capabilities')),
        sa.UniqueConstraint('provider', 'language_code', name='uq_provider_language')
    )
    op.create_index(op.f('ix_provider_capabilities_id'), 'provider_capabilities', ['id'], unique=False)
    op.create_index(op.f('ix_provider_capabilities_language_code'), 'provider_capabilities', ['language_code'], unique=False)
    op.create_index(op.f('ix_provider_capabilities_provider'), 'provider_capabilities', ['provider'], unique=False)

    # 4. Create voice_language_capabilities table
    op.create_table(
        'voice_language_capabilities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('voice_id', sa.Integer(), nullable=False),
        sa.Column('language_code', sa.String(length=10), nullable=False),
        sa.Column('supported', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['language_code'], ['languages.code'], name=op.f('fk_voice_language_capabilities_language_code_languages'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['voice_id'], ['voices.id'], name=op.f('fk_voice_language_capabilities_voice_id_voices'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_voice_language_capabilities')),
        sa.UniqueConstraint('voice_id', 'language_code', name='uq_voice_language')
    )
    op.create_index(op.f('ix_voice_language_capabilities_id'), 'voice_language_capabilities', ['id'], unique=False)
    op.create_index(op.f('ix_voice_language_capabilities_language_code'), 'voice_language_capabilities', ['language_code'], unique=False)
    op.create_index(op.f('ix_voice_language_capabilities_voice_id'), 'voice_language_capabilities', ['voice_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema to initial architecture."""
    op.drop_index(op.f('ix_voice_language_capabilities_voice_id'), table_name='voice_language_capabilities')
    op.drop_index(op.f('ix_voice_language_capabilities_language_code'), table_name='voice_language_capabilities')
    op.drop_index(op.f('ix_voice_language_capabilities_id'), table_name='voice_language_capabilities')
    op.drop_table('voice_language_capabilities')

    op.drop_index(op.f('ix_provider_capabilities_provider'), table_name='provider_capabilities')
    op.drop_index(op.f('ix_provider_capabilities_language_code'), table_name='provider_capabilities')
    op.drop_index(op.f('ix_provider_capabilities_id'), table_name='provider_capabilities')
    op.drop_table('provider_capabilities')

    op.drop_index(op.f('ix_voices_provider_voice_id'), table_name='voices')
    op.drop_column('voices', 'metadata')
    op.drop_column('voices', 'provider_voice_id')

    op.drop_column('languages', 'updated_at')
    op.drop_column('languages', 'metadata')
    op.drop_column('languages', 'direction')
