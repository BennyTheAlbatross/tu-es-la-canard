"""Generate the original Hellfeather March loop using only Python's stdlib."""

import math
import random
import struct
import wave
from pathlib import Path


RATE = 22050
BPM = 150
STEP = 60 / BPM / 4
STEPS = 512
OUTPUT = Path(__file__).with_name("hellfeather_march.wav")

# Original E-minor chromatic riff. Values are MIDI notes; None is a rest.
RIFF_A = [40, 40, 52, 40, 43, 42, 40, None, 40, 47, 46, 43, 42, 40, 35, 39]
RIFF_B = [40, 40, 55, 52, 50, 47, 46, None, 43, 46, 47, 50, 46, 43, 42, 35]
RIFF_C = [40, None, 40, 43, 47, 46, 43, 40, 35, 35, 47, 46, 43, 42, 39, None]
RIFF_D = [52, 50, 47, 46, 43, 46, 47, 50, 52, 55, 54, 50, 47, 46, 43, 39]
PHRASES = (RIFF_A, RIFF_B, RIFF_A, RIFF_C, RIFF_D, RIFF_C, RIFF_B, RIFF_A)


def frequency(note):
    return 440.0 * 2 ** ((note - 69) / 12)


def guitar(phase):
    raw = sum(math.sin(phase * harmonic) / harmonic for harmonic in range(1, 7))
    return math.tanh(raw * 2.7)


def envelope(position, length, attack=0.015, release=0.055):
    return min(1.0, position / attack, max(0.0, (length - position) / release))


def generate():
    random.seed(616)
    total_samples = round(STEPS * STEP * RATE)
    samples = [0.0] * total_samples

    for step in range(STEPS):
        start = round(step * STEP * RATE)
        end = min(total_samples, round((step + 1) * STEP * RATE))
        riff = PHRASES[(step // 16) % len(PHRASES)]
        note = riff[step % 16]
        for index in range(start, end):
            t = index / RATE
            local = (index - start) / RATE
            value = 0.0

            if note is not None:
                root = frequency(note)
                env = envelope(local, STEP)
                value += guitar(math.tau * root * t) * 0.25 * env
                value += guitar(math.tau * root * 1.498 * t) * 0.10 * env
                value += math.sin(math.tau * (root / 2) * t) * 0.20 * env

            # Four-on-the-floor kick with an extra double hit at phrase ends.
            if step % 4 == 0 or step % 16 == 15:
                decay = math.exp(-local * 24)
                sweep = 48 + 90 * math.exp(-local * 35)
                value += math.sin(math.tau * sweep * local) * decay * 0.52

            # Snare on beats two/four; deterministic noise keeps regeneration stable.
            if step % 8 in (4,):
                value += (random.random() * 2 - 1) * math.exp(-local * 18) * 0.32

            # Tight metallic hat on every eighth note.
            if step % 2 == 0:
                value += (random.random() * 2 - 1) * math.exp(-local * 70) * 0.10

            samples[index] += value

    peak = max(abs(value) for value in samples) or 1.0
    scale = 0.88 * 32767 / peak
    with wave.open(str(OUTPUT), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(RATE)
        output.writeframes(b"".join(struct.pack("<h", int(value * scale)) for value in samples))
    print(f"Generated {OUTPUT} ({STEPS * STEP:.1f}s seamless loop)")


if __name__ == "__main__":
    generate()
