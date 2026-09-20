from typing import Dict, Any, List, Optional
import re


# Canonical RAG Lore and Acoustic Signature Knowledge Base for Bloop Voices
VOICE_RAG_CORPUS: Dict[str, Dict[str, Any]] = {
    "normal-male": {
        "character_name": "Normal Male",
        "canonical_source": "Standard Reference Voice - North American Male",
        "persona_summary": "Natural, clear, articulate American English male studio voice.",
        "lore_text": "High-fidelity standard American English male speech synthesis.",
        "vocal_signature": {
            "base_pitch_hz": 0,
            "base_rate_pct": 0,
            "cadence": "steady, authoritative, balanced baritone cadence",
            "timbre": "resonant, clear chest baritone",
            "catchphrases": [],
        },
        "acoustic_dsp": {
            "filter_type": "natural_warmth",
            "bass_boost_db": 1.5,
            "cutoff_hz": 2800,
            "room_reverb_ms": 12,
            "wet_mix": 0.12,
        },
    },
    "normal-female": {
        "character_name": "Normal Female",
        "canonical_source": "Standard Reference Voice - North American Female",
        "persona_summary": "Natural, clear, articulate American English female studio voice.",
        "lore_text": "High-fidelity natural American English female speech synthesis.",
        "vocal_signature": {
            "base_pitch_hz": 0,
            "base_rate_pct": 0,
            "cadence": "natural, articulate, balanced cadence",
            "timbre": "warm, clear soprano studio narration",
            "catchphrases": [],
        },
        "acoustic_dsp": {
            "filter_type": "natural_warmth",
            "bass_boost_db": 1.2,
            "cutoff_hz": 3200,
            "room_reverb_ms": 12,
            "wet_mix": 0.12,
        },
    },
    "dynamic-voice-en-female": {
        "character_name": "Dynamic Female (En)",
        "canonical_source": "Studio Reference Voice - North American Female",
        "persona_summary": "Clear, natural, professional English studio voice.",
        "lore_text": "High-fidelity natural English female speech synthesis.",
        "vocal_signature": {
            "base_pitch_hz": 5,
            "base_rate_pct": 0,
            "cadence": "natural, articulate, balanced cadence",
            "timbre": "warm, clear soprano/alto studio narration",
            "catchphrases": [],
        },
        "acoustic_dsp": {
            "filter_type": "natural_warmth",
            "bass_boost_db": 1.5,
            "cutoff_hz": 3200,
            "room_reverb_ms": 15,
            "wet_mix": 0.15,
        },
    },
    "dynamic-voice-en-male": {
        "character_name": "Dynamic Male (En)",
        "canonical_source": "Studio Reference Voice - North American Male",
        "persona_summary": "Crisp, authoritative, professional English male studio voice.",
        "lore_text": "High-fidelity natural English male speech synthesis.",
        "vocal_signature": {
            "base_pitch_hz": -10,
            "base_rate_pct": 0,
            "cadence": "steady, authoritative, balanced baritone cadence",
            "timbre": "resonant, clear chest baritone",
            "catchphrases": [],
        },
        "acoustic_dsp": {
            "filter_type": "natural_warmth",
            "bass_boost_db": 2.0,
            "cutoff_hz": 2800,
            "room_reverb_ms": 15,
            "wet_mix": 0.15,
        },
    },
    "dynamic-voice-gb-female": {
        "character_name": "Dynamic Female (UK)",
        "canonical_source": "Studio Reference Voice - British Received Pronunciation",
        "persona_summary": "Articulate, refined British English studio voice.",
        "lore_text": "High-fidelity British English speech synthesis.",
        "vocal_signature": {
            "base_pitch_hz": 4,
            "base_rate_pct": -2,
            "cadence": "refined, measured, classical British cadence",
            "timbre": "crisp, elegant, clear articulation",
            "catchphrases": [],
        },
        "acoustic_dsp": {
            "filter_type": "natural_warmth",
            "bass_boost_db": 1.2,
            "cutoff_hz": 3400,
            "room_reverb_ms": 14,
            "wet_mix": 0.15,
        },
    },
    "dynamic-voice-es-neutral": {
        "character_name": "Dynamic Spanish",
        "canonical_source": "Studio Reference Voice - Castilian / International Spanish",
        "persona_summary": "Warm, fluent, expressive Spanish speech synthesis.",
        "lore_text": "High-fidelity Castilian and international Spanish voice synthesis.",
        "vocal_signature": {
            "base_pitch_hz": 2,
            "base_rate_pct": 5,
            "cadence": "melodic, expressive Spanish syllable-timed rhythm",
            "timbre": "bright, warm, open vowels",
            "catchphrases": [],
        },
        "acoustic_dsp": {
            "filter_type": "natural_warmth",
            "bass_boost_db": 1.0,
            "cutoff_hz": 3000,
            "room_reverb_ms": 12,
            "wet_mix": 0.15,
        },
    },
    "dynamic-voice-fr-neutral": {
        "character_name": "Dynamic French",
        "canonical_source": "Studio Reference Voice - Parisian French",
        "persona_summary": "Fluid, melodic, authentic French studio voice.",
        "lore_text": "High-fidelity standard French speech synthesis.",
        "vocal_signature": {
            "base_pitch_hz": 3,
            "base_rate_pct": 2,
            "cadence": "fluid, gentle syllable transitions",
            "timbre": "smooth, resonant nasal vowel balance",
            "catchphrases": [],
        },
        "acoustic_dsp": {
            "filter_type": "natural_warmth",
            "bass_boost_db": 1.0,
            "cutoff_hz": 3100,
            "room_reverb_ms": 14,
            "wet_mix": 0.15,
        },
    },
    "dynamic-voice-de-neutral": {
        "character_name": "Dynamic German",
        "canonical_source": "Studio Reference Voice - Standard German Hochdeutsch",
        "persona_summary": "Structured, precise, clean German studio baritone.",
        "lore_text": "High-fidelity standard German speech synthesis.",
        "vocal_signature": {
            "base_pitch_hz": -8,
            "base_rate_pct": -2,
            "cadence": "structured, rhythmic, distinct consonant articulation",
            "timbre": "grounded, clear, articulate baritone",
            "catchphrases": [],
        },
        "acoustic_dsp": {
            "filter_type": "natural_warmth",
            "bass_boost_db": 1.8,
            "cutoff_hz": 2900,
            "room_reverb_ms": 15,
            "wet_mix": 0.15,
        },
    },
    "dynamic-voice-hi-neutral": {
        "character_name": "Dynamic Hindi",
        "canonical_source": "Studio Reference Voice - Standard Devanagari Hindi",
        "persona_summary": "Warm, lyrical, clear Hindi studio narration voice.",
        "lore_text": "High-fidelity natural Hindi speech synthesis.",
        "vocal_signature": {
            "base_pitch_hz": 6,
            "base_rate_pct": 4,
            "cadence": "lyrical, flowing, authentic aspirated phonetics",
            "timbre": "warm, gentle, melodious Devanagari vocal resonance",
            "catchphrases": [],
        },
        "acoustic_dsp": {
            "filter_type": "natural_warmth",
            "bass_boost_db": 1.2,
            "cutoff_hz": 3200,
            "room_reverb_ms": 16,
            "wet_mix": 0.15,
        },
    },
}


# Canonical Audio & Video Grounded Reference Database for bloop voices
VOICE_AUDIO_VIDEO_REFS: Dict[str, Dict[str, Any]] = {
    "normal-male": {
        "media_title": "Broadcast Studio Reference - US Male",
        "clip_timestamp": "Master Studio Session (00:00 - 02:00)",
        "scene_context": "Calibrated broadcast studio with balanced low-frequency presence.",
        "acoustic_benchmark": {
            "f0_median_hz": 115.0,
            "formant_f1_hz": 480,
            "formant_f2_hz": 1350,
            "tempo_wpm": 125,
            "vocal_grit": 0.05,
            "spatial_acoustic": "Treated vocal booth",
        },
    },
    "normal-female": {
        "media_title": "Broadcast Studio Reference - US Female",
        "clip_timestamp": "Master Studio Session (00:00 - 02:00)",
        "scene_context": "Calibrated studio environment with neutral acoustic response.",
        "acoustic_benchmark": {
            "f0_median_hz": 210.0,
            "formant_f1_hz": 680,
            "formant_f2_hz": 2150,
            "tempo_wpm": 130,
            "vocal_grit": 0.04,
            "spatial_acoustic": "Anechoic vocal chamber",
        },
    },
    "dynamic-voice-en-female": {
        "media_title": "Broadcast Studio Reference - US Female",
        "clip_timestamp": "Master Studio Session (00:00 - 02:00)",
        "scene_context": "Calibrated studio environment with neutral acoustic response.",
        "acoustic_benchmark": {
            "f0_median_hz": 210.0,
            "formant_f1_hz": 680,
            "formant_f2_hz": 2150,
            "tempo_wpm": 130,
            "vocal_grit": 0.04,
            "spatial_acoustic": "Anechoic vocal chamber",
        },
    },
    "dynamic-voice-en-male": {
        "media_title": "Broadcast Studio Reference - US Male",
        "clip_timestamp": "Master Studio Session (00:00 - 02:00)",
        "scene_context": "Calibrated broadcast studio with balanced low-frequency presence.",
        "acoustic_benchmark": {
            "f0_median_hz": 115.0,
            "formant_f1_hz": 480,
            "formant_f2_hz": 1350,
            "tempo_wpm": 125,
            "vocal_grit": 0.06,
            "spatial_acoustic": "Treated vocal booth",
        },
    },
    "dynamic-voice-gb-female": {
        "media_title": "BBC Radio Reference Archive - UK RP",
        "clip_timestamp": "London Studio Session (00:00 - 02:00)",
        "scene_context": "Crisp acoustic studio with British RP clarity.",
        "acoustic_benchmark": {
            "f0_median_hz": 215.0,
            "formant_f1_hz": 670,
            "formant_f2_hz": 2200,
            "tempo_wpm": 122,
            "vocal_grit": 0.03,
            "spatial_acoustic": "Broadcasting suite",
        },
    },
    "dynamic-voice-es-neutral": {
        "media_title": "RTVE Spanish Reference Archive",
        "clip_timestamp": "Madrid Studio Broadcast (00:00 - 02:00)",
        "scene_context": "Madrid recording studio with natural Castilian cadence.",
        "acoustic_benchmark": {
            "f0_median_hz": 200.0,
            "formant_f1_hz": 650,
            "formant_f2_hz": 2100,
            "tempo_wpm": 135,
            "vocal_grit": 0.05,
            "spatial_acoustic": "Acoustically damped booth",
        },
    },
    "dynamic-voice-fr-neutral": {
        "media_title": "Radio France Studio Reference Archive",
        "clip_timestamp": "Parisian Studio Broadcast (00:00 - 02:00)",
        "scene_context": "Parisian broadcast studio with smooth harmonic decay.",
        "acoustic_benchmark": {
            "f0_median_hz": 195.0,
            "formant_f1_hz": 620,
            "formant_f2_hz": 2050,
            "tempo_wpm": 128,
            "vocal_grit": 0.04,
            "spatial_acoustic": "Treated studio booth",
        },
    },
    "dynamic-voice-de-neutral": {
        "media_title": "Deutschlandfunk Studio Benchmark Archive",
        "clip_timestamp": "Cologne Documentary Studio (00:00 - 02:00)",
        "scene_context": "Berlin recording stage with precise Hochdeutsch phonetic articulation.",
        "acoustic_benchmark": {
            "f0_median_hz": 112.0,
            "formant_f1_hz": 490,
            "formant_f2_hz": 1320,
            "tempo_wpm": 118,
            "vocal_grit": 0.06,
            "spatial_acoustic": "Calibrated German broadcasting suite",
        },
    },
    "dynamic-voice-hi-neutral": {
        "media_title": "All India Radio (Akashvani) Studio Benchmark Archive",
        "clip_timestamp": "New Delhi National Broadcast (00:00 - 02:00)",
        "scene_context": "Akashvani Bhavan studio in New Delhi with warm, clear Devanagari phonetics.",
        "acoustic_benchmark": {
            "f0_median_hz": 205.0,
            "formant_f1_hz": 720,
            "formant_f2_hz": 2260,
            "tempo_wpm": 125,
            "vocal_grit": 0.05,
            "spatial_acoustic": "Treated Indian national broadcasting studio",
        },
    },
}


class VoiceRAGService:
    """
    Voice Retrieval-Augmented Generation (RAG) Service.
    Indexes canonical speech patterns and acoustic directives.
    Retrieves and contextualizes prompts with acoustic knowledge.
    """

    def __init__(self):
        self.corpus = VOICE_RAG_CORPUS

    def get_voice_profile(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """Direct lookup for voice profile by voice identifier."""
        return self.corpus.get(voice_id.lower())

    def retrieve_augmented_context(self, voice_id: str, prompt_text: str) -> Dict[str, Any]:
        """
        RAG retrieval step:
        Finds the voice profile, matches semantic keywords against catchphrases and lore,
        and constructs an augmented persona representation for quantum statevector analysis.
        """
        voice_key = voice_id.lower()
        profile = self.corpus.get(voice_key)

        # Fallback profile if voice not specifically indexed
        if not profile:
            fallback_av_ref = {
                "media_title": "Standard Acoustic Model Reference",
                "scene_timestamp": "Baseline Studio Recording",
                "clip_timestamp": "Baseline Studio Recording",
                "scene_context": f"Baseline neural acoustic profile calibrated for {voice_id}.",
                "acoustic_benchmark": {
                    "f0_median_hz": 120.0,
                    "formant_f1_hz": 500,
                    "formant_f2_hz": 1500,
                    "tempo_wpm": 120,
                    "vocal_grit": 0.1,
                    "spatial_acoustic": "Anechoic Studio",
                },
            }
            return {
                "character_name": voice_id.replace("-", " ").title(),
                "canonical_source": "Standard Acoustic Model",
                "audio_video_reference": fallback_av_ref,
                "persona_summary": f"Voice synthesis for {voice_id}",
                "lore_text": prompt_text,
                "matched_catchphrases": [],
                "keyword_resonance_score": 0.0,
                "vocal_signature": {
                    "base_pitch_hz": 0,
                    "base_rate_pct": 0,
                    "cadence": "natural",
                    "timbre": "neutral",
                    "catchphrases": [],
                },
                "acoustic_dsp": {
                    "filter_type": "natural_warmth",
                    "wet_mix": 0.15,
                },
            }

        # Analyze prompt resonance with voice signature & lore
        prompt_lower = prompt_text.lower()
        tokens = set(re.findall(r"\b\w+\b", prompt_lower))

        matched_phrases = []
        for phrase in profile["vocal_signature"].get("catchphrases", []):
            if phrase in prompt_lower or any(word in tokens for word in phrase.split()):
                matched_phrases.append(phrase)

        # Keyword resonance score in [0.0, 1.0]
        resonance_score = min(len(matched_phrases) * 0.35, 1.0)

        # Retrieve media reference and ensure scene_timestamp is normalized
        raw_ref = VOICE_AUDIO_VIDEO_REFS.get(voice_key)
        if raw_ref:
            av_ref = dict(raw_ref)
            ts = av_ref.get("scene_timestamp") or av_ref.get("clip_timestamp") or "Canonical Scene"
            av_ref["scene_timestamp"] = ts
            av_ref["clip_timestamp"] = ts
        else:
            av_ref = {
                "media_title": profile["canonical_source"],
                "scene_timestamp": "Archival Canonical Cut",
                "clip_timestamp": "Archival Canonical Cut",
                "scene_context": profile["persona_summary"],
                "acoustic_benchmark": {
                    "f0_median_hz": 120.0,
                    "formant_f1_hz": 520,
                    "formant_f2_hz": 1400,
                    "tempo_wpm": 120,
                    "vocal_grit": 0.2,
                    "spatial_acoustic": "Studio vocal booth",
                },
            }

        return {
            "character_name": profile["character_name"],
            "canonical_source": profile["canonical_source"],
            "audio_video_reference": av_ref,
            "persona_summary": profile["persona_summary"],
            "lore_text": profile["lore_text"],
            "matched_catchphrases": matched_phrases,
            "keyword_resonance_score": round(resonance_score, 3),
            "vocal_signature": profile["vocal_signature"],
            "acoustic_dsp": profile["acoustic_dsp"],
        }
