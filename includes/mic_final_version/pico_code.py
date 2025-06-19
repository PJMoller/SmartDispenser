import audiobusio
import board
import array
import wifi
import socketpool
import binascii
import gc
import time
import math
import microcontroller
import cyw43
import ipaddress
import adafruit_requests as requests

# --- Configuration ---
WIFI_SSID = "***" # my own home wifi 
WIFI_PASSWORD = "***" # my own home wifi password
FLASK_SERVER = "http://192.168.68.102:5000/transcribe"  # temporary test IP

SAMPLE_RATE = 16000
RECORD_DURATION = 0.5  # seconds
BUFFER_SIZE = int(SAMPLE_RATE * RECORD_DURATION)
SILENCE_THRESHOLD = 100
SILENCE_HYSTERESIS = 1.2
LOW_SOUND_HISTORY = 3

def check_memory(label):
    gc.collect() # garbage collection for more memory
    print(f"{label}: Free={gc.mem_free()}")

def connect_wifi():
    if wifi.radio.connected:
        return
    print("Connecting WiFi...")
    try:
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        print(f"Connected! IP: {wifi.radio.ipv4_address}")
    except Exception as e:
        print(f"WiFi connection failed: {e}")
    cyw43.set_power_management(cyw43.PM_PERFORMANCE) # tried performance mode for better connection stability, did not work
    print("WiFi power management set to Performance mode.")

def calculate_rms(values):
    mean = sum(values) / len(values)
    sum_squares = sum((s - mean) ** 2 for s in values)
    return math.sqrt(sum_squares / len(values)) # root mean square

def record_audio(mic, audio_buffer):
    print(f"Recording {RECORD_DURATION} second at 16kHz...")
    mic.record(audio_buffer, BUFFER_SIZE)
    if max(audio_buffer) == 0:
        print("WARNING: Audio buffer is all zeros!") # aka problem with the mic
    rms = calculate_rms(audio_buffer)
    print(f"Audio RMS: {rms:.2f}")
    return audio_buffer, rms, time.monotonic()

def transcribe_audio1(audio_data): # http request using requests library
    audio_bytes = bytes(audio_data)
    audio_base64 = binascii.b2a_base64(audio_bytes, newline=False).decode('utf-8')
    print("Sending audio to server...")
    try:
        pool = socketpool.SocketPool(wifi.radio)
        http = requests.Session(pool) # use requests library for the http request
        print("Preparing HTTP POST...")
        response = http.post(FLASK_SERVER, json={"audio": audio_base64})
        print("Request sent. Waiting for response...")
        print("Raw response:", response.text)
        result = response.json()
        response.close()
        if "transcript" in result:
            return result["transcript"]
        elif "error" in result:
            return "Error: " + result["error"]
        else:
            return "Unexpected response: " + str(result)
    except Exception as e:
        print(f"Transcription error: {e}")
        return "Transcription error: " + str(e)


def transcribe_audio(audio_data): # manual http sending without requests library
    print("Before encoding request: Free=", gc.mem_free())
    gc.collect()
    print("After GC: Free=", gc.mem_free())
    
    # Encode audio
    audio_bytes = bytes(audio_data)
    audio_base64 = binascii.b2a_base64(audio_bytes, newline=False).decode('utf-8')
    print("After encoding: Free=", gc.mem_free())
    
    # Build payload
    payload = f'{{"audio":"{audio_base64}"}}'
    print("After payload: Free=", gc.mem_free())
    
    try:
        pool = socketpool.SocketPool(wifi.radio)
        sock = pool.socket()
        sock.settimeout(30)
        sock.connect(("192.168.68.102", 5000))
        # manually send http request so that we can use less memory
        # Send headers
        headers = (
            "POST /transcribe HTTP/1.1\r\n"
            "Host: 192.168.68.102:5000\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(payload)}\r\n"
            "\r\n"
        )
        sock.send(headers.encode('utf-8'))
        
        # Send payload
        sock.send(payload.encode('utf-8'))
        
        # Receive response
        response_buffer = bytearray(1024)
        bytes_read = sock.recv_into(response_buffer)
        response = response_buffer[:bytes_read].decode('utf-8')
        print("Raw response:", response)
        sock.close()
        return "Response received"
    except Exception as e:
        print(f"Transcription error: {e}")
        return str(e)





def test_server_connection():
    try:
        pool = socketpool.SocketPool(wifi.radio)
        http = requests.Session(pool)
        response = http.get("http://192.168.68.102:5000/")
        print("Server response:", response.text)
        response.close()
    except Exception as e:
        print("Connection test failed:", e)

# main allocations 
check_memory("Before buffer allocation")
mic = audiobusio.PDMIn(board.GP3, board.GP2, sample_rate=SAMPLE_RATE, bit_depth=16)
connect_wifi()
test_server_connection()
audio_buffer = array.array('H', [0] * BUFFER_SIZE)
gc.collect()
check_memory("After buffer allocation")

rms_history = []

while True: # main loop
    try:
        audio, rms_value, _ = record_audio(mic, audio_buffer)
        rms_history.append(rms_value)
        if len(rms_history) > LOW_SOUND_HISTORY:
            rms_history.pop(0)
        avg_rms = sum(rms_history) / len(rms_history)

        if avg_rms > (SILENCE_THRESHOLD * SILENCE_HYSTERESIS):
            print("Sufficient audio detected. Transcribing...")
            check_memory("Before transcription")
            transcript = transcribe_audio(audio_buffer)
            print("Transcript:", transcript)
        elif avg_rms < (SILENCE_THRESHOLD / SILENCE_HYSTERESIS):
            print("Silence confirmed. Skipping transcription.")
        else:
            print("Ambiguous audio level. Waiting...")

        print("Cycle complete. Waiting...")
        time.sleep(5)

    except Exception as e:
        print(f"A critical error occurred in the main loop: {e}")
        print("Resetting in 10 seconds...")
        time.sleep(10)
        microcontroller.reset()

