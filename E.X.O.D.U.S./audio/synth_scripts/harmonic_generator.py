#!/usr/bin/env python3
"""
Harmonic Generator - Audio Synthesis for E.X.O.D.U.S. Protocol
Generates theta waves, binaural beats, and encoded tonal broadcasts
"""

import numpy as np
import json
import struct
import wave
from typing import Optional
from dataclasses import dataclass

# Constants
SAMPLE_RATE = 48000
BIT_DEPTH = 24
CHANNELS = 2


@dataclass
class FrequencyConfig:
    """Configuration for frequency generation"""
    hz: float
    waveform: str = "sine"
    amplitude: float = 0.8
    phase: float = 0.0


class HarmonicGenerator:
    """
    Generates harmonic audio frequencies for E.X.O.D.U.S. deployment.
    Supports theta waves, binaural beats, and cultural frequency encoding.
    """

    def __init__(self, sample_rate: int = SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.waveform_generators = {
            "sine": self._sine_wave,
            "triangle": self._triangle_wave,
            "square": self._square_wave,
            "sawtooth": self._sawtooth_wave
        }

    def _sine_wave(self, t: np.ndarray, freq: float, amplitude: float, phase: float) -> np.ndarray:
        """Generate sine wave"""
        return amplitude * np.sin(2 * np.pi * freq * t + phase)

    def _triangle_wave(self, t: np.ndarray, freq: float, amplitude: float, phase: float) -> np.ndarray:
        """Generate triangle wave"""
        return amplitude * 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - amplitude

    def _square_wave(self, t: np.ndarray, freq: float, amplitude: float, phase: float) -> np.ndarray:
        """Generate square wave"""
        return amplitude * np.sign(np.sin(2 * np.pi * freq * t + phase))

    def _sawtooth_wave(self, t: np.ndarray, freq: float, amplitude: float, phase: float) -> np.ndarray:
        """Generate sawtooth wave"""
        return amplitude * 2 * (t * freq - np.floor(0.5 + t * freq))

    def generate_tone(self, config: FrequencyConfig, duration_seconds: float) -> np.ndarray:
        """Generate a single tone based on configuration"""
        t = np.linspace(0, duration_seconds, int(self.sample_rate * duration_seconds), False)
        generator = self.waveform_generators.get(config.waveform, self._sine_wave)
        return generator(t, config.hz, config.amplitude, config.phase)

    def generate_theta_wave(self, duration_seconds: float = 60, base_freq: float = 7.0) -> np.ndarray:
        """
        Generate theta wave (4-8 Hz) for deep meditation and ancestral connection.
        Uses binaural beat technique with carrier frequencies.
        """
        t = np.linspace(0, duration_seconds, int(self.sample_rate * duration_seconds), False)

        # Carrier frequencies for binaural beat
        carrier_left = 200  # Hz
        carrier_right = 200 + base_freq  # Hz (creates 7Hz binaural beat)

        # Generate stereo signal
        left_channel = 0.5 * np.sin(2 * np.pi * carrier_left * t)
        right_channel = 0.5 * np.sin(2 * np.pi * carrier_right * t)

        # Stack as stereo
        stereo = np.stack([left_channel, right_channel], axis=1)

        return stereo

    def generate_schumann_resonance(self, duration_seconds: float = 60) -> np.ndarray:
        """
        Generate Schumann resonance (7.83 Hz) for planetary harmonic alignment.
        """
        return self.generate_theta_wave(duration_seconds, 7.83)

    def generate_isochronic_pulse(
        self,
        duration_seconds: float,
        pulse_freq: float = 7.0,
        carrier_freq: float = 200,
        duty_cycle: float = 0.5
    ) -> np.ndarray:
        """
        Generate isochronic tones - pulsed tones at specific frequency.
        More effective than binaural beats for some applications.
        """
        t = np.linspace(0, duration_seconds, int(self.sample_rate * duration_seconds), False)

        # Carrier tone
        carrier = np.sin(2 * np.pi * carrier_freq * t)

        # Pulse envelope
        pulse_period = 1.0 / pulse_freq
        pulse_on_time = pulse_period * duty_cycle
        envelope = np.zeros_like(t)

        for i, time in enumerate(t):
            cycle_position = time % pulse_period
            if cycle_position < pulse_on_time:
                # Smooth fade in/out within pulse
                if cycle_position < pulse_on_time * 0.1:
                    envelope[i] = cycle_position / (pulse_on_time * 0.1)
                elif cycle_position > pulse_on_time * 0.9:
                    envelope[i] = (pulse_on_time - cycle_position) / (pulse_on_time * 0.1)
                else:
                    envelope[i] = 1.0

        # Apply envelope to carrier
        signal = carrier * envelope * 0.7

        # Convert to stereo
        stereo = np.stack([signal, signal], axis=1)

        return stereo

    def generate_432hz_base(self, duration_seconds: float = 60) -> np.ndarray:
        """
        Generate 432 Hz tone - natural tuning foundation.
        432 Hz is considered more harmonically aligned with nature.
        """
        config = FrequencyConfig(hz=432, amplitude=0.5)
        mono = self.generate_tone(config, duration_seconds)

        # Add subtle harmonics
        harmonics = [
            FrequencyConfig(hz=432 * 2, amplitude=0.15),  # Octave
            FrequencyConfig(hz=432 * 3, amplitude=0.08),  # Fifth
            FrequencyConfig(hz=432 * 4, amplitude=0.04),  # Double octave
        ]

        for harmonic in harmonics:
            mono += self.generate_tone(harmonic, duration_seconds)

        # Normalize
        mono = mono / np.max(np.abs(mono)) * 0.7

        # Convert to stereo
        stereo = np.stack([mono, mono], axis=1)

        return stereo

    def mix_frequencies(self, *signals: np.ndarray, weights: Optional[list] = None) -> np.ndarray:
        """Mix multiple frequency signals together"""
        if weights is None:
            weights = [1.0 / len(signals)] * len(signals)

        mixed = np.zeros_like(signals[0])
        for signal, weight in zip(signals, weights):
            mixed += signal * weight

        # Normalize to prevent clipping
        max_val = np.max(np.abs(mixed))
        if max_val > 0:
            mixed = mixed / max_val * 0.9

        return mixed

    def apply_fade(self, signal: np.ndarray, fade_in_seconds: float, fade_out_seconds: float) -> np.ndarray:
        """Apply fade in and fade out to signal"""
        fade_in_samples = int(fade_in_seconds * self.sample_rate)
        fade_out_samples = int(fade_out_seconds * self.sample_rate)

        # Create fade envelopes
        fade_in = np.linspace(0, 1, fade_in_samples)
        fade_out = np.linspace(1, 0, fade_out_samples)

        # Apply fades
        if len(signal.shape) == 2:
            # Stereo
            signal[:fade_in_samples, :] *= fade_in[:, np.newaxis]
            signal[-fade_out_samples:, :] *= fade_out[:, np.newaxis]
        else:
            # Mono
            signal[:fade_in_samples] *= fade_in
            signal[-fade_out_samples:] *= fade_out

        return signal

    def encode_adinkra_cipher(self, signal: np.ndarray, cipher_name: str = "Sankofa") -> np.ndarray:
        """
        Encode Adinkra cipher into audio signal as subtle frequency modulation.
        This is a symbolic encoding for cultural signature purposes.
        """
        # Cipher frequency signatures
        cipher_signatures = {
            "Sankofa": [7, 14, 21],  # Multiples of 7 (return cycles)
            "Gye Nyame": [9, 18, 27],  # Multiples of 9 (divine completion)
            "Aya": [5, 10, 15]  # Multiples of 5 (endurance)
        }

        freqs = cipher_signatures.get(cipher_name, cipher_signatures["Sankofa"])

        # Add subtle frequency layers
        duration = len(signal) / self.sample_rate
        t = np.linspace(0, duration, len(signal), False)

        for freq in freqs:
            modulation = 0.02 * np.sin(2 * np.pi * freq * t)
            if len(signal.shape) == 2:
                signal[:, 0] += modulation
                signal[:, 1] += modulation
            else:
                signal += modulation

        return signal

    def save_wav(self, signal: np.ndarray, filename: str):
        """Save signal as WAV file"""
        # Normalize to 16-bit range
        signal_normalized = signal / np.max(np.abs(signal)) * 32767

        # Convert to int16
        signal_int = signal_normalized.astype(np.int16)

        # Determine channels
        if len(signal.shape) == 2:
            channels = signal.shape[1]
        else:
            channels = 1
            signal_int = signal_int.reshape(-1, 1)

        # Write WAV file
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(signal_int.tobytes())

        print(f"Saved: {filename}")


def main():
    """Generate example harmonic frequencies"""
    import argparse

    parser = argparse.ArgumentParser(description="Harmonic Generator for E.X.O.D.U.S.")
    parser.add_argument("--output", "-o", default="theta_7hz.wav", help="Output filename")
    parser.add_argument("--duration", "-d", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--frequency", "-f", type=float, default=7.0, help="Base frequency (Hz)")
    parser.add_argument("--type", "-t", choices=["theta", "schumann", "isochronic", "432hz"],
                        default="theta", help="Type of frequency to generate")
    parser.add_argument("--cipher", "-c", default="Sankofa", help="Adinkra cipher encoding")

    args = parser.parse_args()

    generator = HarmonicGenerator()

    print(f"Generating {args.type} frequency at {args.frequency}Hz...")

    if args.type == "theta":
        signal = generator.generate_theta_wave(args.duration, args.frequency)
    elif args.type == "schumann":
        signal = generator.generate_schumann_resonance(args.duration)
    elif args.type == "isochronic":
        signal = generator.generate_isochronic_pulse(args.duration, args.frequency)
    elif args.type == "432hz":
        signal = generator.generate_432hz_base(args.duration)

    # Apply fade
    signal = generator.apply_fade(signal, 5, 5)

    # Encode cipher
    signal = generator.encode_adinkra_cipher(signal, args.cipher)

    # Save
    generator.save_wav(signal, args.output)

    print(f"Generated {args.duration}s of {args.type} wave with {args.cipher} cipher")
    print("Activation phrase: The seed was never broken. Only buried.")


if __name__ == "__main__":
    main()
