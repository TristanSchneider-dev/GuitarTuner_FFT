import pyaudio
import numpy as np
import time
from scipy.fft import fft, fftfreq

RATE = 44100
CHUNK = 2 ** 14  # Fidelity
CHANNELS = 1  # Mono
FORMAT = pyaudio.paInt16
BUFFER_SIZE = 10

GUITAR_STRINGS = {
    "E1": 82.41,
    "A": 110.00,
    "D": 146.83,
    "G": 196.00,
    "B": 247.68,
    "E2": 331.00,
}

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

dominant_frequencies = []

def get_dominant_frequency(data, rate):
    N = len(data)
    fft_result = fft(data)
    fft_freq = fftfreq(N, 1 / rate)

    positive_freqs = fft_freq[:N // 2]
    positive_amplitudes = np.abs(fft_result)[:N // 2]

    max_amplitude = 0
    dominant_freq = 0

    for i in range(len(positive_freqs)):
        if positive_amplitudes[i] > max_amplitude:
            max_amplitude = positive_amplitudes[i]
            dominant_freq = positive_freqs[i]

    return dominant_freq

def get_harmonics(base_freq, num_harmonics=5):
    harmonics = []
    for i in range(1, num_harmonics + 1):
        harmonics.append(base_freq * i)
    return harmonics

def get_guitar_string_for_frequency(dominant_freq):
    closest_string = None
    closest_diff = float('inf')

    for string, freq in GUITAR_STRINGS.items():
        harmonics = get_harmonics(freq)

        for harmonic in harmonics:
            diff = abs(dominant_freq - harmonic)
            if diff < closest_diff:
                closest_diff = diff
                closest_string = string

    return closest_string

while True:
    data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
    dominant_freq = get_dominant_frequency(data, RATE)
    guitar_string = get_guitar_string_for_frequency(dominant_freq)
    dominant_frequencies.append(dominant_freq)

    print("Dominante Frequenz: {:.2f} Hz, Gitarrensaite: {}".format(dominant_freq, guitar_string))

    time.sleep(0.1)

stream.stop_stream()
stream.close()
p.terminate()
