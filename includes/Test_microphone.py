import audiobusio
import board
import array
import math
import time

SAMPLE_RATE = 16000
BUFFER_SIZE = 128

mic = audiobusio.PDMIn(
    board.GP3,
    board.GP2,
    sample_rate=SAMPLE_RATE,
    bit_depth=16
)

samples = array.array('H', [0] * BUFFER_SIZE)

def calculate_rms(buffer): # Root of Mean Square of audio samples
    mean_value = sum(buffer) / len(buffer)
    sum_squares = sum((s - mean_value) ** 2 for s in buffer)
    return math.sqrt(sum_squares / len(buffer))

try:
    while True:
        mic.record(samples, len(samples))
        sound_level = calculate_rms(samples)
        print(f"Sound Level: {sound_level:.1f}  ")
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Test stopped by user")

