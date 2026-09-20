"""
Unit tests for Bloop Centralized Core Configuration (Settings).
Tests environment profiles, production safety validators, secret masking,
test isolation checks, and backward-compatibility aliases.
"""

import logging
import pytest
from pydantic import ValidationError
from backend.app.core.config import Settings
from backend.app.core.logging import SecretMaskingFilter


class TestConfigurationProfiles:
    """Test runtime profiles and configuration loading."""

    def test_default_development_profile_loads(self):
        """Validates that default settings instantiate with development defaults."""
        settings = Settings(
            APP_ENV="development",
            APP_DEBUG=True,
            DATABASE_URL="sqlite:///./bloop.db",
            JWT_SECRET_KEY="dev-insecure-secret-key-32characters-minimum-for-testing",
        )
        assert settings.APP_ENV == "development"
        assert settings.APP_DEBUG is True
        assert settings.APP_NAME == "Bloop"
        assert settings.API_V1_PREFIX == "/api/v1"
        assert settings.QUANTUM_ENABLED is True
        assert isinstance(settings.cors_origins, list)
        assert "http://localhost:5173" in settings.cors_origins

    def test_environment_normalization(self):
        """Validates that environment names like 'testing' normalize to 'test' and 'prod' to 'production'."""
        s1 = Settings(APP_ENV="testing", DATABASE_URL="sqlite:///./test.db")
        assert s1.APP_ENV == "test"

        s2 = Settings(
            APP_ENV="prod",
            APP_DEBUG=False,
            DATABASE_URL="postgresql+psycopg2://u:p@db.host.internal:5432/bloop",
            JWT_SECRET_KEY="a" * 32,
            CORS_ORIGINS=["https://bloop.vercel.app"],
        )
        assert s2.APP_ENV == "production"

    def test_backward_compatibility_aliases(self):
        """Verifies that legacy property accessors map seamlessly to canonical names."""
        settings = Settings(
            APP_ENV="development",
            APP_DEBUG=True,
            API_V1_PREFIX="/api/v1",
            JWT_SECRET_KEY="dev-insecure-secret-key-32characters-minimum-for-testing",
            CORS_ORIGINS="http://localhost:5173,http://localhost:3000",
        )
        assert settings.ENVIRONMENT == settings.APP_ENV
        assert settings.DEBUG == settings.APP_DEBUG
        assert settings.API_V1_STR == settings.API_V1_PREFIX
        assert settings.SECRET_KEY == settings.JWT_SECRET_KEY
        assert settings.BACKEND_CORS_ORIGINS == settings.CORS_ORIGINS
        assert len(settings.cors_origins) == 2


class TestProductionSafetySafeguards:
    """Tests that production mode enforces strict fail-fast security rules."""

    def test_production_rejects_debug_enabled(self):
        """Production must fail fast if APP_DEBUG=True."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                APP_ENV="production",
                APP_DEBUG=True,
                DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/db",
                JWT_SECRET_KEY="a" * 32,
                CORS_ORIGINS=["https://bloop.vercel.app"],
            )
        assert "APP_DEBUG must be False in production mode" in str(exc_info.value)

    def test_production_rejects_sqlite_database(self):
        """Production must fail fast if DATABASE_URL is SQLite."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                APP_ENV="production",
                APP_DEBUG=False,
                DATABASE_URL="sqlite:///./bloop.db",
                JWT_SECRET_KEY="a" * 32,
                CORS_ORIGINS=["https://bloop.vercel.app"],
            )
        assert "Production requires a persistent PostgreSQL DATABASE_URL" in str(exc_info.value)

    def test_production_rejects_insecure_jwt_secret(self):
        """Production must fail fast if JWT_SECRET_KEY is weak or a default dev placeholder."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                APP_ENV="production",
                APP_DEBUG=False,
                DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/db",
                JWT_SECRET_KEY="dev-insecure-secret-key-32characters-minimum-for-testing",
                CORS_ORIGINS=["https://bloop.vercel.app"],
            )
        assert "JWT_SECRET_KEY must be a cryptographically secure secret" in str(exc_info.value)

    def test_production_rejects_short_jwt_secret(self):
        """Production must reject secrets shorter than 32 characters."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                APP_ENV="production",
                APP_DEBUG=False,
                DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/db",
                JWT_SECRET_KEY="short-secret-key",
                CORS_ORIGINS=["https://bloop.vercel.app"],
            )
        assert "JWT_SECRET_KEY must be a cryptographically secure secret" in str(exc_info.value)

    def test_production_rejects_wildcard_cors(self):
        """Production must reject wildcard CORS ('*')."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                APP_ENV="production",
                APP_DEBUG=False,
                DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/db",
                JWT_SECRET_KEY="a" * 32,
                CORS_ORIGINS="*",
            )
        assert "Wildcard CORS ('*') is prohibited in production" in str(exc_info.value)

    def test_production_accepts_valid_configuration(self):
        """Valid production configuration must instantiate without error."""
        settings = Settings(
            APP_ENV="production",
            APP_DEBUG=False,
            DATABASE_URL="postgresql+psycopg2://prod_user:SuperSecretP@ss123@dpg-abc.render.com:5432/bloop_db",
            JWT_SECRET_KEY="b" * 64,
            CORS_ORIGINS=["https://bloop.vercel.app"],
            ELEVENLABS_API_KEY="sk_live_validkeyfortesting",
        )
        assert settings.APP_ENV == "production"
        assert settings.APP_DEBUG is False
        assert "https://bloop.vercel.app" in settings.cors_origins


class TestTestIsolationSafeguards:
    """Tests that test runs cannot accidentally target production infrastructure."""

    def test_test_environment_rejects_production_database(self):
        """APP_ENV=test must fail immediately if DATABASE_URL contains production hostnames."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                APP_ENV="test",
                DATABASE_URL="postgresql+psycopg2://user:pass@dpg-prod-instance.render.com:5432/bloop_prod",
            )
        assert "Automated tests detected a production database URL" in str(exc_info.value)

    def test_test_environment_accepts_isolated_sqlite_db(self):
        """APP_ENV=test accepts isolated test database."""
        settings = Settings(
            APP_ENV="test",
            DATABASE_URL="sqlite:///./test_bloop.db",
        )
        assert settings.APP_ENV == "test"
        assert settings.DATABASE_URL == "sqlite:///./test_bloop.db"


class TestSecretMasking:
    """Tests that secrets are scrubbed from string representations and logging."""

    def test_settings_repr_masks_secrets(self):
        """__repr__ and __str__ must never print raw secrets."""
        settings = Settings(
            APP_ENV="development",
            DATABASE_URL="postgresql+psycopg2://user:supersecretpass@host:5432/db",
            JWT_SECRET_KEY="my-confidential-jwt-secret-key-32chars",
            ELEVENLABS_API_KEY="sk_live_1234567890abcdef",
        )
        repr_output = repr(settings)
        assert "supersecretpass" not in repr_output
        assert "my-confidential-jwt-secret-key-32chars" not in repr_output
        assert "sk_live_1234567890abcdef" not in repr_output
        assert "***" in repr_output
        assert "***MASKED***" in repr_output

    def test_secret_masking_filter_scrubs_log_records(self):
        """SecretMaskingFilter must replace sensitive values with ***MASKED***."""
        secret = "secret-token-to-hide-1234"
        masking_filter = SecretMaskingFilter([secret])

        record = logging.LogRecord(
            name="bloop.test",
            level=logging.INFO,
            pathname=__file__,
            lineno=10,
            msg=f"Calling external service with token {secret} now.",
            args=(),
            exc_info=None,
        )

        assert masking_filter.filter(record) is True
        assert secret not in record.msg
        assert "***MASKED***" in record.msg


class TestQuantumSubsystemIndependence:
    """Tests that Quantum Intelligence can be toggled without breaking core settings."""

    def test_quantum_can_be_disabled(self):
        """QUANTUM_ENABLED=False must be a valid configuration."""
        settings = Settings(
            APP_ENV="development",
            QUANTUM_ENABLED=False,
        )
        assert settings.QUANTUM_ENABLED is False
        assert settings.APP_NAME == "Bloop"
