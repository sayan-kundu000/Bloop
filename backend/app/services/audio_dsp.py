import io
import math
import wave
from typing import Dict, Any, Optional
import numpy as np
import scipy.signal as signal
import miniaudio

from backend.app.core.logging import logger


class AudioDSPService:
    """
    Digital Signal Processing (DSP) Acoustic Transformation Service.
    Applies character-specific acoustic profiles, equalizer curves, metallic comb filters,
    and spatial resonance to synthesized speech.
    """

    def apply_character_dsp(
        self,
        audio_bytes: bytes,
        dsp_profile: Dict[str, Any],
    ) -> tuple[bytes, str]:
        """
        Takes raw audio bytes (MP3 or WAV), applies the character's DSP acoustic filter,
        and returns the processed 16-bit PCM WAV bytes and audio format ('wav').
        """
        filter_type = dsp_profile.get("filter_type", "natural_warmth")
        if not audio_bytes or len(audio_bytes) < 100:
            return audio_bytes, "mp3"

        try:
            # 1. Decode audio bytes into float32 array
            sample_rate = 24000
            if audio_bytes.startswith(b"RIFF"):
                with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
                    sample_rate = wf.getframerate()
                    nchannels = wf.getnchannels()
                    frames = wf.readframes(wf.getnframes())
                    samples_int16 = np.frombuffer(frames, dtype=np.int16)
                    if nchannels > 1:
                        samples_int16 = samples_int16.reshape(-1, nchannels).mean(axis=1).astype(np.int16)
                    raw_samples = samples_int16.astype(np.float32)
            else:
                decoded = miniaudio.decode(audio_bytes, nchannels=1, sample_rate=24000)
                sample_rate = decoded.sample_rate
                raw_samples = np.array(decoded.samples, dtype=np.float32)

            if len(raw_samples) == 0:
                return audio_bytes, "mp3"

            # Normalize to [-1.0, 1.0] range
            max_val = np.max(np.abs(raw_samples))
            if max_val > 1.0:
                samples = raw_samples / 32768.0
            else:
                samples = raw_samples

            # 2. Dispatch to specific acoustic DSP filter
            processed = self._dispatch_filter(samples, sample_rate, filter_type, dsp_profile)

            # 3. Soft Limiter & Headroom Normalization
            processed = np.clip(processed, -1.0, 1.0)
            peak = np.max(np.abs(processed))
            if peak > 0.95:
                processed = processed * (0.95 / peak)

            # 4. Encode to 16-bit PCM WAV
            pcm_int16 = (processed * 32767.0).astype(np.int16)
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(pcm_int16.tobytes())

            wav_buffer.seek(0)
            out_bytes = wav_buffer.read()
            logger.info(
                f"DSP filter '{filter_type}' successfully applied: "
                f"{len(audio_bytes)} bytes input -> {len(out_bytes)} bytes WAV output"
            )
            return out_bytes, "wav"

        except Exception as e:
            logger.warning(f"Audio DSP processing encountered error ({e}), returning original audio.")
            return audio_bytes, "mp3"

    def _dispatch_filter(
        self,
        x: np.ndarray,
        sr: int,
        filter_type: str,
        params: Dict[str, Any],
    ) -> np.ndarray:
        wet_mix = float(params.get("wet_mix", 0.35))

        if filter_type == "dark_knight_sub_bass":
            # Batman / Maximus / Russian: Low-shelf sub-bass boost + dark chamber reflection
            boost_db = float(params.get("bass_boost_db", 8.0))
            cutoff = float(params.get("cutoff_hz", 120))
            y = self._apply_low_shelf(x, sr, cutoff, boost_db)
            # Reverb reflection
            delay_samples = int(sr * 0.028)  # 28ms room slapback
            if len(y) > delay_samples:
                reverb_tail = np.zeros_like(y)
                reverb_tail[delay_samples:] = y[:-delay_samples] * 0.28
                y = y + reverb_tail
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "latverian_comb_filter":
            # Doctor Doom: Metallic titanium mask comb resonance
            delay_ms = float(params.get("delay_ms", 3.4))
            feedback = float(params.get("feedback", 0.46))
            delay_samples = max(int(sr * (delay_ms / 1000.0)), 1)
            y = np.copy(x)
            for i in range(delay_samples, len(x)):
                y[i] = x[i] + feedback * y[i - delay_samples]
            # Subtle bandpass around human speech for hollow helmet acoustic
            sos = signal.butter(2, [180, 4800], btype="bandpass", fs=sr, output="sos")
            y = signal.sosfilt(sos, y)
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "spectral_ghost_reverb":
            # Monjulika / Big Chill: Haunting ethereal multi-tap feedback delay
            delay_ms = float(params.get("delay_ms", 150))
            decay = float(params.get("decay", 0.60))
            d1 = int(sr * (delay_ms / 1000.0))
            d2 = int(sr * ((delay_ms * 1.6) / 1000.0))
            y = np.copy(x)
            if len(y) > d1:
                y[d1:] += x[:-d1] * decay
            if len(y) > d2:
                y[d2:] += x[:-d2] * (decay * 0.5)
            # High-frequency damping for ghostly dissipation
            sos = signal.butter(2, 2800, btype="lowpass", fs=sr, output="sos")
            y = signal.sosfilt(sos, y)
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "righteous_overdrive":
            # Sunny Deol / Ravana / Rath / Tuco: Soft-clipping saturation + sub-bass body
            drive = float(params.get("drive", 2.0))
            boost_db = float(params.get("bass_boost_db", 6.0))
            y = np.tanh(x * drive)
            if boost_db > 0:
                y = self._apply_low_shelf(y, sr, 140, boost_db)
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "manic_jitter_exciter":
            # Joker / Green Goblin: High-frequency exciter + phase jitter
            sos = signal.butter(2, [2800, 6500], btype="bandpass", fs=sr, output="sos")
            highs = signal.sosfilt(sos, x)
            highs_excited = np.tanh(highs * 2.2)
            y = x + (highs_excited * 0.4)
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "cid_radio_broadcast":
            # ACP Pradyuman / Anup Soni: Telephone/walkie-talkie broadcast bandpass
            low = float(params.get("low_cutoff", 280))
            high = float(params.get("high_cutoff", 3600))
            sos = signal.butter(2, [low, high], btype="bandpass", fs=sr, output="sos")
            y = signal.sosfilt(sos, x)
            # Mild broadcast compression
            y = np.tanh(y * 1.3)
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "anime_formant_boost":
            # Pikachu / Helium: High-shelf formant boost
            sos = signal.butter(2, 3800, btype="highpass", fs=sr, output="sos")
            highs = signal.sosfilt(sos, x)
            y = x + (highs * 0.8)
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "debonair_velvet":
            # Krishna / Lucifer / Arijit Singh: Smooth 2nd-harmonic warming + hall space
            sos = signal.butter(2, 6000, btype="lowpass", fs=sr, output="sos")
            smoothed = signal.sosfilt(sos, x)
            harmonics = np.clip(smoothed + 0.15 * (smoothed ** 2), -1.0, 1.0)
            # Gentle divine hall decay
            delay_samples = int(sr * 0.038)
            if len(harmonics) > delay_samples:
                harmonics[delay_samples:] += harmonics[:-delay_samples] * 0.22
            return (1.0 - wet_mix) * x + wet_mix * harmonics

        elif filter_type == "sultry_whisper_compressor":
            # Thomas Shelby / Shakuni / Nikki: Close-mic intimate compression
            y = np.sign(x) * (np.abs(x) ** 0.65)
            sos = signal.butter(2, 200, btype="highpass", fs=sr, output="sos")
            y = signal.sosfilt(sos, y)
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "saiyan_power_distortion":
            # Vegeta: Fierce 2nd-order harmonic distortion + aggressive mid bark
            drive = float(params.get("drive", 2.8))
            mid_boost = float(params.get("mid_boost_db", 5.5))
            # Mid-range emphasis before saturation
            sos_mid = signal.butter(2, [1200, 3800], btype="bandpass", fs=sr, output="sos")
            mids = signal.sosfilt(sos_mid, x)
            y = np.tanh((x + mids * 0.6) * drive)
            if mid_boost > 0:
                y = y + mids * (10.0 ** (mid_boost / 20.0) - 1.0) * 0.3
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "rap_punch_compressor":
            # Eminem: Hyper-compressed rapid punch with presence boost
            y = np.sign(x) * (np.abs(x) ** 0.55)  # Fast RMS compression
            sos = signal.butter(2, [2400, 5200], btype="bandpass", fs=sr, output="sos")
            presence = signal.sosfilt(sos, x)
            y = y + presence * 0.45
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "pirate_rum_swagger":
            # Jack Sparrow: Micro-warble + warm tavern room reflection
            delay_samples = int(sr * (float(params.get("room_reflection_ms", 32)) / 1000.0))
            y = np.copy(x)
            if len(y) > delay_samples:
                y[delay_samples:] += x[:-delay_samples] * 0.32
            # Subtle low-mid warmth
            sos = signal.butter(2, 240, btype="lowpass", fs=sr, output="sos")
            warmth = signal.sosfilt(sos, x)
            y = y + warmth * 0.25
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "commander_parade_reverb":
            # Erwin Smith: Massive parade-ground reverberant projection
            delay1 = int(sr * 0.045)
            delay2 = int(sr * 0.085)
            y = np.copy(x)
            if len(y) > delay1:
                y[delay1:] += x[:-delay1] * 0.35
            if len(y) > delay2:
                y[delay2:] += x[:-delay2] * 0.22
            # 1.5kHz projection horn boost
            sos = signal.butter(2, [1000, 3200], btype="bandpass", fs=sr, output="sos")
            projection = signal.sosfilt(sos, x)
            y = y + projection * 0.35
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "keynote_auditorium_presence":
            # Steve Jobs: Intimate lavalier mic + large keynote hall slapback
            slap = int(sr * (float(params.get("slapback_ms", 36)) / 1000.0))
            y = np.copy(x)
            if len(y) > slap:
                y[slap:] += x[:-slap] * 0.26
            # Crystal clear 4kHz acoustic sheen
            sos = signal.butter(2, [3000, 6000], btype="bandpass", fs=sr, output="sos")
            sheen = signal.sosfilt(sos, x)
            y = y + sheen * 0.28
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "stark_intercom_comb":
            # Robert Downey Jr. / Iron Man: Armored HUD intercom bandpass & light comb
            comb_delay = int(sr * 0.0025)
            y = np.copy(x)
            for i in range(comb_delay, len(x)):
                y[i] = x[i] + 0.30 * y[i - comb_delay]
            sos = signal.butter(2, [350, 4800], btype="bandpass", fs=sr, output="sos")
            y = signal.sosfilt(sos, y)
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "comedic_crisp_articulator":
            # Chatur Silencer / South Indian / BB Ki Vines: High-frequency crisp transient enhancer
            sos = signal.butter(2, 3400, btype="highpass", fs=sr, output="sos")
            crisp = signal.sosfilt(sos, x)
            y = x + crisp * 0.50
            return (1.0 - wet_mix) * x + wet_mix * y

        elif filter_type == "natural_warmth":
            # Analog console warmth: 250Hz gentle warmth + 15ms room reflection
            warmth_db = float(params.get("bass_boost_db", 2.0))
            y = self._apply_low_shelf(x, sr, 250.0, warmth_db)
            delay_ms = float(params.get("room_reverb_ms", 15.0))
            delay_samples = max(int(sr * (delay_ms / 1000.0)), 1)
            if len(y) > delay_samples:
                y[delay_samples:] += x[:-delay_samples] * 0.15
            return (1.0 - wet_mix) * x + wet_mix * y

        else:
            return x

    def _apply_low_shelf(self, x: np.ndarray, sr: int, cutoff: float, boost_db: float) -> np.ndarray:
        """Applies a second-order low-shelf boost filter."""
        gain = 10.0 ** (boost_db / 20.0)
        sos = signal.butter(2, cutoff, btype="lowpass", fs=sr, output="sos")
        lows = signal.sosfilt(sos, x)
        return x + lows * (gain - 1.0)
