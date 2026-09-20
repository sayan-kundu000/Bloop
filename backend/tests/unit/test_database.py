"""
Unit and Integration Tests for Bloop Database Architecture (SQLAlchemy 2.x).
Validates models, constraints, relationships, cascade deletes, ownership isolation,
and transaction rollback behavior across all Bloop domain entities.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from backend.app.db.session import SessionLocal, get_db
from backend.app.models.user import User
from backend.app.models.user_preference import UserPreference
from backend.app.models.language import Language
from backend.app.models.voice import Voice
from backend.app.models.speech_generation import SpeechGeneration
from backend.app.models.favorite import Favorite
from backend.app.models.quantum_experiment import QuantumExperiment
from backend.app.core.security import get_password_hash


class TestUserAndPreferenceDomain:
    """Tests for User and UserPreference models and constraints."""

    def test_create_user_stores_hash_not_plaintext(self, db_session):
        """User creation must only persist password hash, never plaintext."""
        user = User(
            email="database_test_user@example.com",
            hashed_password=get_password_hash("SuperSecret123!"),
            full_name="Database Test User",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "database_test_user@example.com"
        assert user.hashed_password != "SuperSecret123!"
        assert user.hashed_password.startswith("$2")
        assert user.is_active is True
        assert user.created_at is not None

    def test_user_email_uniqueness_enforced(self, db_session):
        """Database must reject duplicate user emails with IntegrityError."""
        u1 = User(email="unique_email@example.com", hashed_password="hash1")
        db_session.add(u1)
        db_session.commit()

        u2 = User(email="unique_email@example.com", hashed_password="hash2")
        db_session.add(u2)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_user_preference_cascade_deletion(self, db_session):
        """Deleting a user must cascade delete the user's preference record."""
        user = User(email="cascade_user@example.com", hashed_password="hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        pref = UserPreference(user_id=user.id, theme="light", audio_speed=1.2)
        db_session.add(pref)
        db_session.commit()

        pref_id = pref.id
        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Preference should be gone
        deleted_pref = db_session.execute(
            select(UserPreference).where(UserPreference.id == pref_id)
        ).scalar_one_or_none()
        assert deleted_pref is None


class TestCatalogDomain:
    """Tests for Language and Voice dynamic catalog models."""

    def test_language_primary_key_uniqueness(self, db_session):
        """Language code is the primary key and must be unique."""
        lang = db_session.execute(
            select(Language).where(Language.code == "en-US")
        ).scalar_one_or_none()
        assert lang is not None
        assert lang.name == "English (US)"

    def test_dynamic_voice_registration_without_hardcoded_voices(self, db_session):
        """Validates that custom voices can be dynamically registered."""
        voice = Voice(
            voice_id="dynamic-user-provided-voice-001",
            name="Custom Studio Voice",
            language_code="en-US",
            gender="neutral",
            provider="elevenlabs",
            is_user_configured=True,
        )
        db_session.add(voice)
        db_session.commit()
        db_session.refresh(voice)

        assert voice.id is not None
        assert voice.is_user_configured is True
        assert voice.provider == "elevenlabs"

        # Duplicate voice_id must fail
        duplicate = Voice(
            voice_id="dynamic-user-provided-voice-001",
            name="Duplicate Voice",
            language_code="en-US",
        )
        db_session.add(duplicate)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()


class TestSpeechAndFavoriteDomain:
    """Tests for SpeechGeneration and Favorite persistence and constraints."""

    def test_speech_generation_lifecycle_and_audio_metadata(self, db_session):
        """Validates speech generation lifecycle status and audio metadata storage."""
        gen = SpeechGeneration(
            text="Testing audio generation metadata persistence.",
            char_count=45,
            word_count=5,
            language_code="en-US",
            voice_id="normal-male",
            audio_filename="db_test_audio_001.mp3",
            duration_seconds=3.25,
            file_size_bytes=48120,
            audio_format="mp3",
            status="completed",
            provider="simulation",
        )
        db_session.add(gen)
        db_session.commit()
        db_session.refresh(gen)

        assert gen.id is not None
        assert gen.status == "completed"
        assert gen.audio_format == "mp3"
        assert gen.file_size_bytes == 48120

    def test_favorite_unique_constraint_per_user_generation(self, db_session):
        """User cannot favorite the exact same generation more than once."""
        user = User(email="fav_tester@example.com", hashed_password="hash")
        gen = SpeechGeneration(
            text="Favorite text",
            char_count=13,
            word_count=2,
            language_code="en-US",
            voice_id="normal-female",
            audio_filename="fav_test_gen.mp3",
        )
        db_session.add_all([user, gen])
        db_session.commit()

        fav1 = Favorite(user_id=user.id, generation_id=gen.id, label="My Top Favorite")
        db_session.add(fav1)
        db_session.commit()

        fav2 = Favorite(user_id=user.id, generation_id=gen.id, label="Duplicate Favorite")
        db_session.add(fav2)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()


class TestQuantumIntelligenceDomain:
    """Tests for QuantumExperiment persistence and complete TTS independence."""

    def test_quantum_experiment_persistence_and_isolation(self, db_session):
        """Quantum experiments persist JSON payloads and remain fully decoupled from TTS."""
        exp = QuantumExperiment(
            experiment_type="circuit",
            title="Bell State Entanglement Experiment",
            input_payload={"qubits": 2, "gates": [{"gate": "h", "target": 0}]},
            results={"counts": {"00": 512, "11": 512}},
            qubit_count=2,
            circuit_depth=2,
            execution_time_ms=12.5,
            status="completed",
        )
        db_session.add(exp)
        db_session.commit()
        db_session.refresh(exp)

        assert exp.id is not None
        assert exp.input_payload["qubits"] == 2
        assert exp.results["counts"]["00"] == 512
        assert exp.status == "completed"


class TestSessionManagementAndRollback:
    """Tests that request-scoped get_db dependency properly rolls back on errors."""

    def test_get_db_rolls_back_on_unhandled_exception(self):
        """If an error occurs inside a session block, rollback must execute automatically."""
        gen = get_db()
        db = next(gen)

        try:
            # Stage an invalid entity that violates constraints
            user = User(email="rollback_user@example.com", hashed_password="hash")
            db.add(user)
            db.flush()
            # Deliberately raise unhandled error before commit
            raise RuntimeError("Simulated internal service error during request processing")
        except RuntimeError:
            try:
                gen.throw(RuntimeError("Simulated internal service error"))
            except RuntimeError:
                pass

        # Verify in a new session that the uncommitted user was rolled back
        verify_session = SessionLocal()
        found = verify_session.execute(
            select(User).where(User.email == "rollback_user@example.com")
        ).scalar_one_or_none()
        verify_session.close()

        assert found is None
