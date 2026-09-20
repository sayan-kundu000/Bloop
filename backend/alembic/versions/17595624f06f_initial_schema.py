"""initial_schema

Revision ID: 17595624f06f
Revises: 
Create Date: 2026-09-09 11:18:36.391200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17595624f06f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to initial Bloop architecture."""
    # 1. Languages Table
    op.create_table(
        'languages',
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('native_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('code', name=op.f('pk_languages'))
    )
    op.create_index(op.f('ix_languages_code'), 'languages', ['code'], unique=False)

    # 2. Users Table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 3. User Preferences Table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('default_language_code', sa.String(length=10), nullable=True),
        sa.Column('default_voice_id', sa.String(length=100), nullable=True),
        sa.Column('theme', sa.String(length=20), nullable=False, server_default='dark'),
        sa.Column('audio_speed', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('auto_play', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['default_language_code'], ['languages.code'], name=op.f('fk_user_preferences_default_language_code_languages'), ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_user_preferences_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user_preferences')),
        sa.UniqueConstraint('user_id', name=op.f('uq_user_preferences_user_id'))
    )
    op.create_index(op.f('ix_user_preferences_id'), 'user_preferences', ['id'], unique=False)
    op.create_index(op.f('ix_user_preferences_user_id'), 'user_preferences', ['user_id'], unique=True)

    # 4. Voices Table (CRITICAL: Empty catalog, dynamic architecture only)
    op.create_table(
        'voices',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('voice_id', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('language_code', sa.String(length=10), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=False, server_default='unspecified'),
        sa.Column('accent', sa.String(length=50), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='dynamic'),
        sa.Column('preview_url', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('is_user_configured', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['language_code'], ['languages.code'], name=op.f('fk_voices_language_code_languages'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_voices'))
    )
    op.create_index(op.f('ix_voices_id'), 'voices', ['id'], unique=False)
    op.create_index(op.f('ix_voices_language_code'), 'voices', ['language_code'], unique=False)
    op.create_index(op.f('ix_voices_voice_id'), 'voices', ['voice_id'], unique=True)

    # 5. Speech Generations Table (Audio Metadata & Lifecycle Status; No binary audio blobs)
    op.create_table(
        'speech_generations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('char_count', sa.Integer(), nullable=False),
        sa.Column('word_count', sa.Integer(), nullable=False),
        sa.Column('language_code', sa.String(length=10), nullable=False),
        sa.Column('voice_id', sa.String(length=100), nullable=False),
        sa.Column('voice_name', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='completed'),
        sa.Column('audio_filename', sa.String(length=255), nullable=False),
        sa.Column('duration_seconds', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('audio_format', sa.String(length=10), nullable=False, server_default='mp3'),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='elevenlabs'),
        sa.Column('provider_request_id', sa.String(length=100), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_speech_generations_user_id_users'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_speech_generations'))
    )
    op.create_index(op.f('ix_speech_generations_audio_filename'), 'speech_generations', ['audio_filename'], unique=True)
    op.create_index(op.f('ix_speech_generations_created_at'), 'speech_generations', ['created_at'], unique=False)
    op.create_index(op.f('ix_speech_generations_id'), 'speech_generations', ['id'], unique=False)
    op.create_index(op.f('ix_speech_generations_status'), 'speech_generations', ['status'], unique=False)
    op.create_index(op.f('ix_speech_generations_user_id'), 'speech_generations', ['user_id'], unique=False)
    op.create_index('ix_speech_generations_user_created', 'speech_generations', ['user_id', 'created_at'], unique=False)

    # 6. Favorites Table
    op.create_table(
        'favorites',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('generation_id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['generation_id'], ['speech_generations.id'], name=op.f('fk_favorites_generation_id_speech_generations'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_favorites_user_id_users'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_favorites')),
        sa.UniqueConstraint('user_id', 'generation_id', name='uq_user_generation_favorite')
    )
    op.create_index(op.f('ix_favorites_generation_id'), 'favorites', ['generation_id'], unique=False)
    op.create_index(op.f('ix_favorites_id'), 'favorites', ['id'], unique=False)
    op.create_index(op.f('ix_favorites_user_id'), 'favorites', ['user_id'], unique=False)

    # 7. Quantum Experiments Table (Isolated experiment tracking)
    op.create_table(
        'quantum_experiments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('experiment_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='completed'),
        sa.Column('input_payload', sa.JSON(), nullable=False),
        sa.Column('results', sa.JSON(), nullable=False),
        sa.Column('qubit_count', sa.Integer(), nullable=True, server_default='2'),
        sa.Column('circuit_depth', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('execution_time_ms', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('simulator', sa.String(length=50), nullable=True, server_default='qiskit_aer'),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_quantum_experiments_user_id_users'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_quantum_experiments'))
    )
    op.create_index(op.f('ix_quantum_experiments_created_at'), 'quantum_experiments', ['created_at'], unique=False)
    op.create_index(op.f('ix_quantum_experiments_experiment_type'), 'quantum_experiments', ['experiment_type'], unique=False)
    op.create_index(op.f('ix_quantum_experiments_id'), 'quantum_experiments', ['id'], unique=False)
    op.create_index(op.f('ix_quantum_experiments_status'), 'quantum_experiments', ['status'], unique=False)
    op.create_index(op.f('ix_quantum_experiments_user_id'), 'quantum_experiments', ['user_id'], unique=False)
    op.create_index('ix_quantum_experiments_user_created', 'quantum_experiments', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_quantum_experiments_user_created', table_name='quantum_experiments')
    op.drop_index(op.f('ix_quantum_experiments_user_id'), table_name='quantum_experiments')
    op.drop_index(op.f('ix_quantum_experiments_status'), table_name='quantum_experiments')
    op.drop_index(op.f('ix_quantum_experiments_id'), table_name='quantum_experiments')
    op.drop_index(op.f('ix_quantum_experiments_experiment_type'), table_name='quantum_experiments')
    op.drop_index(op.f('ix_quantum_experiments_created_at'), table_name='quantum_experiments')
    op.drop_table('quantum_experiments')

    op.drop_index(op.f('ix_favorites_user_id'), table_name='favorites')
    op.drop_index(op.f('ix_favorites_id'), table_name='favorites')
    op.drop_index(op.f('ix_favorites_generation_id'), table_name='favorites')
    op.drop_table('favorites')

    op.drop_index('ix_speech_generations_user_created', table_name='speech_generations')
    op.drop_index(op.f('ix_speech_generations_user_id'), table_name='speech_generations')
    op.drop_index(op.f('ix_speech_generations_status'), table_name='speech_generations')
    op.drop_index(op.f('ix_speech_generations_id'), table_name='speech_generations')
    op.drop_index(op.f('ix_speech_generations_created_at'), table_name='speech_generations')
    op.drop_index(op.f('ix_speech_generations_audio_filename'), table_name='speech_generations')
    op.drop_table('speech_generations')

    op.drop_index(op.f('ix_voices_voice_id'), table_name='voices')
    op.drop_index(op.f('ix_voices_language_code'), table_name='voices')
    op.drop_index(op.f('ix_voices_id'), table_name='voices')
    op.drop_table('voices')

    op.drop_index(op.f('ix_user_preferences_user_id'), table_name='user_preferences')
    op.drop_index(op.f('ix_user_preferences_id'), table_name='user_preferences')
    op.drop_table('user_preferences')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')

    op.drop_index(op.f('ix_languages_code'), table_name='languages')
    op.drop_table('languages')
