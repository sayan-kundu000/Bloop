import io
import math
import struct
import wave
from typing import Dict, Any, Optional
from backend.app.core.logging import logger
from backend.app.providers.base import TTSProvider

# Comprehensive Neural Voice Mapping for All Bloop Dynamic Voices
VOICE_NEURAL_PROFILES = {
    # --- Characters & Villains ---
    "batman-animated-2000": {"voice": "en-US-ChristopherNeural", "pitch": -25, "rate": -10},
    "joker-animated-2000": {"voice": "en-US-GuyNeural", "pitch": 25, "rate": 15},
    "spider-man": {"voice": "en-US-GuyNeural", "pitch": 12, "rate": 10},
    "green-goblin": {"voice": "en-US-GuyNeural", "pitch": 18, "rate": 15},
    "doctor-doom": {"voice": "en-US-ChristopherNeural", "pitch": -22, "rate": -8},
    "lucifer": {"voice": "en-GB-RyanNeural", "pitch": -10, "rate": -5},
    "maximus-decimus-meredius": {"voice": "en-GB-RyanNeural", "pitch": -20, "rate": -10},
    "tuco-salamanca": {"voice": "en-US-GuyNeural", "pitch": -8, "rate": 15},
    "jack-sparrow": {"voice": "en-GB-ThomasNeural", "pitch": -6, "rate": -5},
    "thomas-shelby": {"voice": "en-GB-RyanNeural", "pitch": -22, "rate": -15},
    "nikki-obsession": {"voice": "en-US-JennyNeural", "pitch": -8, "rate": -12},

    # --- Indian Epic & TV ---
    "ravana": {"voice": "hi-IN-MadhurNeural", "pitch": -28, "rate": -12},
    "shakuni-mahabharat": {"voice": "hi-IN-MadhurNeural", "pitch": 8, "rate": -15},
    "vasudev-krishna": {"voice": "hi-IN-MadhurNeural", "pitch": -4, "rate": -10},
    "acp-pradyuman": {"voice": "hi-IN-MadhurNeural", "pitch": -12, "rate": -5},
    "anup-soni": {"voice": "hi-IN-MadhurNeural", "pitch": -10, "rate": -8},
    "kokila-modi": {"voice": "hi-IN-SwaraNeural", "pitch": -6, "rate": 10},
    "aparichit": {"voice": "hi-IN-MadhurNeural", "pitch": -22, "rate": 6},
    "jaykant-shikre": {"voice": "hi-IN-MadhurNeural", "pitch": -15, "rate": 14},
    "sameer-fuddi": {"voice": "hi-IN-MadhurNeural", "pitch": 24, "rate": 16},
    "titu-mama": {"voice": "hi-IN-MadhurNeural", "pitch": -8, "rate": 12},
    "monjulika": {"voice": "hi-IN-SwaraNeural", "pitch": 15, "rate": -8},
    "rehman-dakait": {"voice": "hi-IN-MadhurNeural", "pitch": -24, "rate": -5},
    "chatur-silencer": {"voice": "hi-IN-MadhurNeural", "pitch": 20, "rate": 20},

    # --- Celebrities & Icons ---
    "sunny-deol": {"voice": "hi-IN-MadhurNeural", "pitch": -18, "rate": 8},
    "narendra-modi": {"voice": "hi-IN-MadhurNeural", "pitch": -10, "rate": -10},
    "mithun-chakraborty": {"voice": "hi-IN-MadhurNeural", "pitch": -8, "rate": 6},
    "navjot-singh-sidhu": {"voice": "hi-IN-MadhurNeural", "pitch": 6, "rate": 22},
    "arijit-singh": {"voice": "hi-IN-MadhurNeural", "pitch": 0, "rate": -5},
    "ravi-kishan": {"voice": "hi-IN-MadhurNeural", "pitch": -5, "rate": 10},
    "cristiano-ronaldo": {"voice": "pt-BR-AntonioNeural", "pitch": 0, "rate": 10},
    "bobby-fischer": {"voice": "en-US-GuyNeural", "pitch": -8, "rate": 5},
    "michael-jackson": {"voice": "en-US-GuyNeural", "pitch": 30, "rate": 0},
    "jim-carrey": {"voice": "en-US-GuyNeural", "pitch": 15, "rate": 20},
    "robert-downey-jr": {"voice": "en-US-GuyNeural", "pitch": -8, "rate": 12},
    "eminem": {"voice": "en-US-GuyNeural", "pitch": -5, "rate": 35},
    "steve-jobs": {"voice": "en-US-GuyNeural", "pitch": -10, "rate": -15},
    "elon-musk": {"voice": "en-US-GuyNeural", "pitch": -12, "rate": -10},

    # --- Accents & Effects ---
    "helium-voice-male": {"voice": "en-US-GuyNeural", "pitch": 65, "rate": 25},
    "helium-voice-female": {"voice": "en-US-JennyNeural", "pitch": 65, "rate": 25},
    "south-indian-male": {"voice": "en-IN-PrabhatNeural", "pitch": -5, "rate": 5},
    "south-indian-female": {"voice": "en-IN-NeerjaNeural", "pitch": 0, "rate": 0},
    "russian-accent-male": {"voice": "ru-RU-DmitryNeural", "pitch": -15, "rate": -5},
    "russian-accent-female": {"voice": "ru-RU-SvetlanaNeural", "pitch": 0, "rate": 0},
    "british-accent-male": {"voice": "en-GB-RyanNeural", "pitch": 0, "rate": 0},
    "british-accent-female": {"voice": "en-GB-SoniaNeural", "pitch": 0, "rate": 0},
    "american-accent-male": {"voice": "en-US-GuyNeural", "pitch": 0, "rate": 0},
    "american-accent-female": {"voice": "en-US-JennyNeural", "pitch": 0, "rate": 0},
    "australian-accent-male": {"voice": "en-AU-WilliamNeural", "pitch": 0, "rate": 0},
    "australian-accent-female": {"voice": "en-AU-NatashaNeural", "pitch": 0, "rate": 0},

    # --- Anime & Cartoons ---
    "pikachu": {"voice": "en-US-JennyNeural", "pitch": 80, "rate": 35},
    "vegeta": {"voice": "en-US-GuyNeural", "pitch": 8, "rate": 10},
    "erwin-smith": {"voice": "en-US-ChristopherNeural", "pitch": -10, "rate": 10},
    "spidermonkey": {"voice": "en-US-GuyNeural", "pitch": 45, "rate": 30},
    "big-chill": {"voice": "en-US-ChristopherNeural", "pitch": -18, "rate": -20},
    "rath": {"voice": "en-US-ChristopherNeural", "pitch": 10, "rate": 20},

    # --- Baseline Dynamic Slots ---
    "normal-male": {"voice": "en-US-GuyNeural", "pitch": 0, "rate": 0},
    "normal-female": {"voice": "en-US-JennyNeural", "pitch": 0, "rate": 0},
    "dynamic-voice-en-female": {"voice": "en-US-JennyNeural", "pitch": 0, "rate": 0},
    "dynamic-voice-en-male": {"voice": "en-US-GuyNeural", "pitch": 0, "rate": 0},
    "dynamic-voice-gb-female": {"voice": "en-GB-SoniaNeural", "pitch": 0, "rate": 0},
    "dynamic-voice-es-neutral": {"voice": "es-ES-ElviraNeural", "pitch": 0, "rate": 0},
    "dynamic-voice-fr-neutral": {"voice": "fr-FR-DeniseNeural", "pitch": 0, "rate": 0},
    "dynamic-voice-de-neutral": {"voice": "de-DE-ConradNeural", "pitch": 0, "rate": 0},
    "dynamic-voice-hi-neutral": {"voice": "hi-IN-SwaraNeural", "pitch": 0, "rate": 0},
}


# Acoustic & Expressive Style Modulation Mapping for All 77 Emotions
EMOTION_ACOUSTIC_PROFILES = {
    "neutral": {"pitch": 0, "rate": 0, "volume": 0, "style": "calm"},
    "happy": {"pitch": 28, "rate": 14, "volume": 10, "style": "cheerful"},
    "joyful": {"pitch": 32, "rate": 16, "volume": 12, "style": "cheerful"},
    "excited": {"pitch": 42, "rate": 24, "volume": 20, "style": "excited"},
    "enthusiastic": {"pitch": 36, "rate": 20, "volume": 15, "style": "excited"},
    "playful": {"pitch": 26, "rate": 12, "volume": 8, "style": "cheerful"},
    "cheerful": {"pitch": 25, "rate": 12, "volume": 10, "style": "cheerful"},
    "amused": {"pitch": 22, "rate": 10, "volume": 8, "style": "cheerful"},
    "delighted": {"pitch": 28, "rate": 14, "volume": 12, "style": "cheerful"},
    "content": {"pitch": -6, "rate": -4, "volume": -5, "style": "friendly"},
    "confident": {"pitch": -14, "rate": 6, "volume": 10, "style": "newscast"},
    "proud": {"pitch": 12, "rate": 6, "volume": 12, "style": "newscast"},
    "triumphant": {"pitch": 38, "rate": 20, "volume": 25, "style": "shouting"},
    "hopeful": {"pitch": 16, "rate": 6, "volume": 6, "style": "hopeful"},
    "grateful": {"pitch": 8, "rate": -6, "volume": -5, "style": "hopeful"},
    "loving": {"pitch": -10, "rate": -12, "volume": -15, "style": "hopeful"},
    "affectionate": {"pitch": -12, "rate": -14, "volume": -18, "style": "hopeful"},
    "romantic": {"pitch": -14, "rate": -16, "volume": -20, "style": "whispering"},
    "seductive": {"pitch": -18, "rate": -20, "volume": -25, "style": "whispering"},
    "flirtatious": {"pitch": 22, "rate": 10, "volume": 6, "style": "cheerful"},
    "charming": {"pitch": 8, "rate": 4, "volume": 4, "style": "friendly"},
    "tender": {"pitch": -12, "rate": -16, "volume": -20, "style": "hopeful"},
    "compassionate": {"pitch": -8, "rate": -12, "volume": -10, "style": "hopeful"},
    "empathetic": {"pitch": -6, "rate": -10, "volume": -8, "style": "hopeful"},
    "calm": {"pitch": -8, "rate": -12, "volume": -10, "style": "calm"},
    "peaceful": {"pitch": -12, "rate": -16, "volume": -15, "style": "calm"},
    "relaxed": {"pitch": -10, "rate": -12, "volume": -10, "style": "calm"},
    "soothing": {"pitch": -12, "rate": -16, "volume": -15, "style": "calm"},
    "comforting": {"pitch": -10, "rate": -12, "volume": -10, "style": "calm"},
    "serious": {"pitch": -20, "rate": -8, "volume": 10, "style": "newscast"},
    "determined": {"pitch": -16, "rate": 8, "volume": 15, "style": "newscast"},
    "assertive": {"pitch": -12, "rate": 10, "volume": 15, "style": "newscast"},
    "authoritative": {"pitch": -22, "rate": -4, "volume": 20, "style": "newscast"},
    "inspirational": {"pitch": 18, "rate": 10, "volume": 15, "style": "newscast"},
    "motivational": {"pitch": 24, "rate": 16, "volume": 18, "style": "newscast"},
    "passionate": {"pitch": 24, "rate": 14, "volume": 18, "style": "excited"},
    "dramatic": {"pitch": 16, "rate": -8, "volume": 15, "style": "newscast"},
    "intense": {"pitch": 18, "rate": 12, "volume": 20, "style": "angry"},
    "urgent": {"pitch": 32, "rate": 28, "volume": 25, "style": "shouting"},
    "angry": {"pitch": 36, "rate": 22, "volume": 30, "style": "angry"},
    "furious": {"pitch": 45, "rate": 32, "volume": 35, "style": "shouting"},
    "annoyed": {"pitch": 18, "rate": 12, "volume": 15, "style": "angry"},
    "frustrated": {"pitch": 20, "rate": 10, "volume": 18, "style": "angry"},
    "impatient": {"pitch": 24, "rate": 24, "volume": 20, "style": "angry"},
    "disappointed": {"pitch": -22, "rate": -16, "volume": -15, "style": "depressed"},
    "sad": {"pitch": -30, "rate": -22, "volume": -20, "style": "sad"},
    "heartbroken": {"pitch": -36, "rate": -26, "volume": -25, "style": "sad"},
    "melancholic": {"pitch": -26, "rate": -22, "volume": -20, "style": "sad"},
    "lonely": {"pitch": -24, "rate": -18, "volume": -20, "style": "sad"},
    "nostalgic": {"pitch": -14, "rate": -12, "volume": -10, "style": "hopeful"},
    "regretful": {"pitch": -22, "rate": -16, "volume": -15, "style": "sad"},
    "guilty": {"pitch": -24, "rate": -16, "volume": -20, "style": "sad"},
    "ashamed": {"pitch": -28, "rate": -20, "volume": -25, "style": "sad"},
    "anxious": {"pitch": 28, "rate": 20, "volume": 15, "style": "terrified"},
    "nervous": {"pitch": 24, "rate": 14, "volume": 10, "style": "terrified"},
    "fearful": {"pitch": 32, "rate": 18, "volume": 18, "style": "terrified"},
    "terrified": {"pitch": 48, "rate": 34, "volume": 28, "style": "terrified"},
    "worried": {"pitch": 18, "rate": 10, "volume": 10, "style": "terrified"},
    "suspicious": {"pitch": -12, "rate": -10, "volume": 0, "style": "unfriendly"},
    "confused": {"pitch": 18, "rate": -6, "volume": 0, "style": "cheerful"},
    "curious": {"pitch": 22, "rate": 8, "volume": 5, "style": "cheerful"},
    "surprised": {"pitch": 38, "rate": 18, "volume": 20, "style": "excited"},
    "amazed": {"pitch": 32, "rate": 12, "volume": 15, "style": "excited"},
    "awe-struck": {"pitch": 10, "rate": -14, "volume": -10, "style": "hopeful"},
    "shocked": {"pitch": 42, "rate": 24, "volume": 25, "style": "shouting"},
    "disgusted": {"pitch": -16, "rate": -10, "volume": 10, "style": "unfriendly"},
    "sarcastic": {"pitch": -12, "rate": -8, "volume": 5, "style": "unfriendly"},
    "teasing": {"pitch": 24, "rate": 10, "volume": 8, "style": "cheerful"},
    "mysterious": {"pitch": -24, "rate": -18, "volume": -25, "style": "whispering"},
    "whispering": {"pitch": -30, "rate": -25, "volume": -40, "style": "whispering"},
    "thoughtful": {"pitch": -12, "rate": -14, "volume": -10, "style": "calm"},
    "wise": {"pitch": -18, "rate": -18, "volume": -10, "style": "calm"},
    "deadpan": {"pitch": -16, "rate": -6, "volume": 0, "style": "calm"},
    "sleepy": {"pitch": -24, "rate": -32, "volume": -30, "style": "calm"},
    "ecstatic": {"pitch": 52, "rate": 32, "volume": 30, "style": "excited"},
    "eager": {"pitch": 28, "rate": 20, "volume": 15, "style": "excited"},
    "skeptical": {"pitch": -8, "rate": -6, "volume": 0, "style": "unfriendly"},
}


class MockTTSProvider(TTSProvider):
    """
    Simulation & High-Fidelity Multi-Voice TTS Provider Adapter.
    Uses Microsoft Edge Neural Voices with voice-specific pitch and rate offsets,
    guaranteeing distinct male, female, character, and accent voices without requiring
    commercial API keys.
    """

    def get_provider_name(self) -> str:
        return "simulation"

    def is_configured(self) -> bool:
        return True

    def _resolve_voice_params(self, voice_id: str, options: Dict[str, Any]) -> tuple[str, str, str, str, Optional[str]]:
        """Resolves the neural voice identifier, pitch offset, rate percentage, volume percentage, and SSML style."""
        profile = VOICE_NEURAL_PROFILES.get(voice_id.lower())
        user_speed = float(options.get("speed") or 1.0)
        user_pitch = float(options.get("pitch") or 1.0)

        # Base offsets from profile
        if profile:
            voice_name = profile["voice"]
            base_pitch = profile["pitch"]
            base_rate = profile["rate"]
        else:
            # Fallback heuristic based on voice_id keywords
            v_lower = voice_id.lower()
            lang = options.get("language", "en-US")
            is_female = "female" in v_lower or "woman" in v_lower
            base_pitch = 0
            base_rate = 0

            if "hi" in lang or any(k in v_lower for k in ["hindi", "india", "deol", "modi"]):
                voice_name = "hi-IN-SwaraNeural" if is_female else "hi-IN-MadhurNeural"
            elif "gb" in lang or "british" in v_lower:
                voice_name = "en-GB-SoniaNeural" if is_female else "en-GB-RyanNeural"
            elif "au" in lang or "australian" in v_lower:
                voice_name = "en-AU-NatashaNeural" if is_female else "en-AU-WilliamNeural"
            elif "ru" in lang or "russian" in v_lower:
                voice_name = "ru-RU-SvetlanaNeural" if is_female else "ru-RU-DmitryNeural"
            else:
                voice_name = "en-US-JennyNeural" if is_female else "en-US-GuyNeural"

        # Emotion-specific pitch, rate, volume, and expressive SSML style
        selected_emotion = str(options.get("emotion") or "neutral").strip().lower()
        emo_profile = EMOTION_ACOUSTIC_PROFILES.get(selected_emotion, {"pitch": 0, "rate": 0, "volume": 0, "style": "calm"})
        emo_pitch = emo_profile.get("pitch", 0)
        emo_rate = emo_profile.get("rate", 0)
        emo_vol = emo_profile.get("volume", 0)
        emo_style = emo_profile.get("style", "calm")

        # If quantum voice modulator supplied calibrated acoustic overrides, incorporate them
        if "pitch_override" in options and "rate_override" in options:
            try:
                q_pitch = int(options["pitch_override"].replace("Hz", ""))
            except ValueError:
                q_pitch = base_pitch
            try:
                q_rate = int(options["rate_override"].replace("%", ""))
            except ValueError:
                q_rate = base_rate
            total_pitch = q_pitch
            total_rate = q_rate
        else:
            pitch_delta = int(round((user_pitch - 1.0) * 40))
            total_pitch = base_pitch + pitch_delta + emo_pitch
            speed_delta = int(round((user_speed - 1.0) * 100))
            total_rate = base_rate + speed_delta + emo_rate

        total_pitch = max(min(total_pitch, 90), -60)
        total_rate = max(min(total_rate, 80), -40)
        emo_vol = max(min(emo_vol, 50), -50)

        pitch_str = f"{total_pitch:+d}Hz"
        rate_str = f"{total_rate:+d}%"
        vol_str = f"{emo_vol:+d}%"

        return voice_name, pitch_str, rate_str, vol_str, emo_style

    async def generate_speech(
        self,
        text: str,
        voice_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bytes:
        options = options or {}
        voice_name, pitch_str, rate_str, vol_str, emo_style = self._resolve_voice_params(voice_id, options)
        selected_emotion = str(options.get("emotion") or "neutral").strip()

        logger.info(
            f"Generating speech with voice '{voice_id}' using Neural Voice '{voice_name}' "
            f"(style={emo_style}, pitch={pitch_str}, rate={rate_str}, volume={vol_str}, emotion={selected_emotion})"
        )

        # Tier 1: Microsoft Edge Neural TTS with Expressive SSML
        try:
            import edge_tts
            xml_lang = options.get("language", "en-US")
            escaped_text = (
                text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;")
            )

            # 1a. Try SSML with expressive style and prosody
            audio_data = bytearray()
            if emo_style and emo_style != "calm":
                ssml = (
                    f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
                    f"xmlns:mstts='https://www.w3.org/2001/mstts' xml:lang='{xml_lang}'>\n"
                    f"  <voice name='{voice_name}'>\n"
                    f"    <mstts:express-as style='{emo_style}'>\n"
                    f"      <prosody pitch='{pitch_str}' rate='{rate_str}' volume='{vol_str}'>\n"
                    f"        {escaped_text}\n"
                    f"      </prosody>\n"
                    f"    </mstts:express-as>\n"
                    f"  </voice>\n"
                    f"</speak>"
                )
                try:
                    communicate = edge_tts.Communicate(ssml, voice=voice_name)
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_data.extend(chunk["data"])
                except Exception as ssml_err:
                    logger.info(f"Style '{emo_style}' not supported on '{voice_name}' ({ssml_err}), falling back to prosody...")
                    audio_data.clear()

            # 1b. Fallback to prosody SSML if style not supported or calm
            if len(audio_data) < 100:
                ssml_prosody = (
                    f"<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='{xml_lang}'>\n"
                    f"  <voice name='{voice_name}'>\n"
                    f"    <prosody pitch='{pitch_str}' rate='{rate_str}' volume='{vol_str}'>\n"
                    f"      {escaped_text}\n"
                    f"    </prosody>\n"
                    f"  </voice>\n"
                    f"</speak>"
                )
                try:
                    communicate = edge_tts.Communicate(ssml_prosody, voice=voice_name)
                    async for chunk in communicate.stream():
                        if chunk["type"] == "audio":
                            audio_data.extend(chunk["data"])
                except Exception as prosody_err:
                    logger.info(f"Prosody SSML failed ({prosody_err}), trying standard communicate...")
                    audio_data.clear()

            # 1c. Direct communicate call fallback
            if len(audio_data) < 100:
                communicate = edge_tts.Communicate(text, voice=voice_name, pitch=pitch_str, rate=rate_str, volume=vol_str)
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data.extend(chunk["data"])

            if len(audio_data) > 100:
                logger.info(f"Successfully synthesized {len(audio_data)} bytes via Edge Neural TTS ({voice_name})")
                return bytes(audio_data)
        except Exception as e:
            logger.warning(f"Edge Neural TTS failed ({e}), falling back to synthesis tone...")

        # Tier 2: Synthesize audio tone matching the character acoustic profile
        return self._synthesize_audio_tone(text, voice_id=voice_id, emotion=selected_emotion)

    def _synthesize_audio_tone(self, text: str, voice_id: str = "", emotion: str = "") -> bytes:
        """
        Synthesizes a distinctive acoustic harmonic tone corresponding to the text length,
        character vocal profile, and emotional delivery as a valid WAV audio stream.
        """
        sample_rate = 22050
        duration = min(max(len(text) * 0.05, 1.0), 5.0)  # 1 to 5 seconds
        num_samples = int(sample_rate * duration)

        v_lower = voice_id.lower()
        if any(k in v_lower for k in ["helium", "pikachu"]):
            base_freq = 660.0  # E5 squeaky chirp
            vibrato_rate = 12.0
            vibrato_depth = 15.0
        elif any(k in v_lower for k in ["batman", "ravana", "doom", "sunny-deol", "big-chill", "rath", "tuco", "shikre", "dakait", "maximus"]):
            base_freq = 110.0  # A2 deep resonant baritone/bass
            vibrato_rate = 4.0
            vibrato_depth = 2.0
        elif any(k in v_lower for k in ["joker", "spidermonkey", "chatur", "fuddi"]):
            base_freq = 440.0  # A4 eccentric / lively
            vibrato_rate = 8.0
            vibrato_depth = 10.0
        elif any(k in v_lower for k in ["krishna", "monjulika", "arijit", "michael-jackson"]):
            base_freq = 261.63  # C4 melodic / peaceful
            vibrato_rate = 5.0
            vibrato_depth = 4.0
        elif "female" in v_lower or any(k in v_lower for k in ["kokila", "nikki"]):
            base_freq = 320.0  # Smooth female timbre
            vibrato_rate = 5.5
            vibrato_depth = 4.0
        else:
            base_freq = 180.0  # Standard warm male voice
            vibrato_rate = 4.5
            vibrato_depth = 3.0

        # Emotion-specific tonal acoustic modulation
        emo_lower = (emotion or "").lower()
        if any(k in emo_lower for k in ["angry", "furious", "intense", "urgent"]):
            base_freq *= 1.25
            vibrato_rate *= 1.4
            vibrato_depth *= 1.5
        elif any(k in emo_lower for k in ["happy", "joyful", "excited", "ecstatic", "cheerful"]):
            base_freq *= 1.18
            vibrato_rate *= 1.3
            vibrato_depth *= 1.3
        elif any(k in emo_lower for k in ["sad", "heartbroken", "melancholic", "lonely", "disappointed"]):
            base_freq *= 0.85
            vibrato_rate *= 0.7
            vibrato_depth *= 0.6
        elif any(k in emo_lower for k in ["whispering", "mysterious", "sleepy", "romantic"]):
            base_freq *= 0.92
            vibrato_rate *= 0.8
            vibrato_depth *= 0.4

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            frames = bytearray()
            for i in range(num_samples):
                t = float(i) / sample_rate
                envelope = min(t * 12, 1.0) * min((duration - t) * 6, 1.0)
                freq = base_freq + vibrato_depth * math.sin(2.0 * math.pi * vibrato_rate * t)
                sample = (
                    0.55 * math.sin(2.0 * math.pi * freq * t) +
                    0.30 * math.sin(2.0 * math.pi * (freq * 1.5) * t) +
                    0.15 * math.sin(2.0 * math.pi * (freq * 2.0) * t)
                )
                sample_val = int(sample * envelope * 22000.0)
                sample_val = max(-32767, min(32767, sample_val))
                frames.extend(struct.pack("<h", sample_val))

            wav_file.writeframes(frames)

        buffer.seek(0)
        return buffer.read()
