"""
Bloop Database Initialization & Baseline Seeding
Initializes relational schema tables and seeds baseline supported ISO languages.
CRITICAL INVARIANT: Never seeds hardcoded or fake voices in production.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import engine, Base
from backend.app.models.capability import VoiceLanguageCapability, ProviderCapability
from backend.app.models.language import Language
from backend.app.models.voice import Voice

STANDARD_LANGUAGES = [
    {"code": "en-US", "name": "English (US)", "native_name": "English"},
    {"code": "en-GB", "name": "English (UK)", "native_name": "British English"},
    {"code": "es-ES", "name": "Spanish (Spain)", "native_name": "Español"},
    {"code": "fr-FR", "name": "French (France)", "native_name": "Français"},
    {"code": "de-DE", "name": "German (Germany)", "native_name": "Deutsch"},
    {"code": "hi-IN", "name": "Hindi (India)", "native_name": "हिन्दी"},
    {"code": "ja-JP", "name": "Japanese (Japan)", "native_name": "日本語"},
    {"code": "it-IT", "name": "Italian (Italy)", "native_name": "Italiano"},
    {"code": "pt-BR", "name": "Portuguese (Brazil)", "native_name": "Português"},
    {"code": "en-AU", "name": "English (Australia)", "native_name": "Australian English"},
    {"code": "ru-RU", "name": "Russian (Russia)", "native_name": "Русский"},
]

# Development & testing-only baseline slots for local simulation testing.
# Production starts with an empty voice catalog; real voices are registered dynamically by the user.
DEV_DYNAMIC_VOICE_TEMPLATES = [
    {
        "voice_id": "normal-male",
        "name": "Normal Male",
        "language_code": "en-US",
        "gender": "male",
        "accent": "American",
        "description": "Standard natural American English male voice.",
        "provider": "dynamic",
        "is_user_configured": False,
    },
    {
        "voice_id": "normal-female",
        "name": "Normal Female",
        "language_code": "en-US",
        "gender": "female",
        "accent": "American",
        "description": "Standard natural American English female voice.",
        "provider": "dynamic",
        "is_user_configured": False,
    },
]

# Backward compatibility alias for test suites
DYNAMIC_VOICE_TEMPLATES = DEV_DYNAMIC_VOICE_TEMPLATES


def init_db(db: Session) -> None:
    """Initializes tables and seeds baseline languages without hardcoded production voices."""
    Base.metadata.create_all(bind=engine)

    # 1. Seed standard ISO languages
    for lang_data in STANDARD_LANGUAGES:
        existing = db.execute(
            select(Language).where(Language.code == lang_data["code"])
        ).scalar_one_or_none()
        if not existing:
            lang = Language(**lang_data)
            db.add(lang)
    db.commit()

    # 2. In production, maintain zero voice records (user provides actual voices)
    if settings.APP_ENV == "production":
        logger.info("Database initialized with standard languages. Voice catalog empty (production mode).")
        return

    # 3. For local development / automated tests only: seed testing slots
    baseline_voice_ids = {v["voice_id"] for v in DEV_DYNAMIC_VOICE_TEMPLATES}
    stale_voices = db.execute(
        select(Voice).where(
            ~Voice.voice_id.in_(baseline_voice_ids),
            Voice.provider == "dynamic",
        )
    ).scalars().all()
    for v in stale_voices:
        db.delete(v)
    db.commit()

    for voice_data in DEV_DYNAMIC_VOICE_TEMPLATES:
        existing = db.execute(
            select(Voice).where(Voice.voice_id == voice_data["voice_id"])
        ).scalar_one_or_none()
        if not existing:
            voice = Voice(**voice_data)
            db.add(voice)
            db.flush()
            target_voice = voice
        else:
            existing.name = voice_data["name"]
            existing.language_code = voice_data["language_code"]
            existing.gender = voice_data["gender"]
            existing.accent = voice_data["accent"]
            existing.description = voice_data["description"]
            existing.is_active = True
            target_voice = existing

        # Ensure VoiceLanguageCapability is linked
        cap_exists = db.execute(
            select(VoiceLanguageCapability).where(
                VoiceLanguageCapability.voice_id == target_voice.id,
                VoiceLanguageCapability.language_code == target_voice.language_code,
            )
        ).scalar_one_or_none()
        if not cap_exists:
            db.add(
                VoiceLanguageCapability(
                    voice_id=target_voice.id,
                    language_code=target_voice.language_code,
                    supported=True,
                    enabled=True,
                )
            )
    db.commit()
    logger.info("Database initialized with standard languages and dynamic voice registry.")

