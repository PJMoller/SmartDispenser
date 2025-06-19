'''
# This is the main flask server code but I couldn't find out what was the problem with the POST method
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

YOUR_GOOGLE_API_KEY = "****"  # Replaced it with stars

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        data = request.json
        audio_base64 = data['audio']
        url = f"https://speech.googleapis.com/v1/speech:recognize?key={YOUR_GOOGLE_API_KEY}"
        payload = {
            "config": {
                "encoding": "LINEAR16",
                "sampleRateHertz": 16000,
                "languageCode": "en-US"
            },
            "audio": {
                "content": audio_base64
            }
        }
        response = requests.post(url, json=payload)
        result = response.json()
        if 'results' in result and len(result['results']) > 0:
            transcript = result['results'][0]['alternatives'][0]['transcript']
            return jsonify({"transcript": transcript})
        return jsonify({"error": "No transcription received"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''

# this is the test version for making sure the Flask server is working and debugging the req handling
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    print("Request headers:", request.headers)
    print("Request content type:", request.content_type)
    print("Request data:", request.data)
    print("Request form:", request.form)
    print("Request args:", request.args)
    try:
        data = request.get_json(force=True)
        print("Parsed JSON:", data)
        if data is None:
            return jsonify({"error": "No JSON data received"}), 400
        audio = data.get('audio', '')
        if not audio:
            return jsonify({"error": "No 'audio' key in JSON"}), 400
        return jsonify({"transcript": f"Received {len(audio)} characters"})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 400

@app.route('/')
def index():
    return "Flask server is running"

if __name__ == '__main__':
    print("updated 7")
    app.run(host='0.0.0.0', port=5000)


