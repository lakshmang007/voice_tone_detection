from flask import Flask, render_template, request, jsonify
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import os
import time
import io
from model.tone_detector import ToneDetector

app = Flask(__name__)
tone_detector = ToneDetector()

# Configuration
SAMPLE_RATE = 16000  # Sample rate in Hz

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_audio():
    """Analyze uploaded audio and predict emotion"""
    try:
        # Get request data - could be form data or JSON
        analysis_id = None
        is_speaking = False

        if request.is_json:
            data = request.get_json()
            analysis_id = data.get('analysisId', 0)
            is_speaking = data.get('isSpeaking', False)
            print(f"Received analysis request #{analysis_id}, isSpeaking: {is_speaking}")

        # If not speaking, return the last emotion or neutral
        if not is_speaking:
            if hasattr(app, 'last_emotion_idx'):
                emotion = tone_detector.emotions[app.last_emotion_idx]
            else:
                # Default to neutral if no previous emotion
                neutral_idx = next((i for i, e in tone_detector.emotions.items()
                                  if e['name'].lower() == 'formal'), 0)
                emotion = tone_detector.emotions[neutral_idx]

            return jsonify({
                'status': 'success',
                'emotion': emotion['name'],
                'emoji': emotion['emoji'],
                'description': emotion['description'],
                'audio_file': 'simulated_recording.wav',
                'analysis_id': analysis_id,
                'is_speaking': is_speaking
            })

        # For demonstration purposes, return a random emotion when speaking
        # In a real implementation, you would analyze the audio data
        import random

        # Use a weighted random selection to make transitions more natural
        # This makes it more likely to stay in the same emotion or move to a similar one
        if hasattr(app, 'last_emotion_idx'):
            # 50% chance to stay in the same emotion
            # 30% chance to move to an adjacent emotion
            # 20% chance to pick a completely random emotion
            r = random.random()
            if r < 0.5:  # Stay the same
                emotion_idx = app.last_emotion_idx
            elif r < 0.8:  # Move to adjacent
                shift = random.choice([-1, 1])
                emotion_idx = (app.last_emotion_idx + shift) % len(tone_detector.emotions)
            else:  # Random
                emotion_idx = random.randint(0, len(tone_detector.emotions) - 1)
        else:
            # First time, pick a random emotion
            emotion_idx = random.randint(0, len(tone_detector.emotions) - 1)

        # Store for next time
        app.last_emotion_idx = emotion_idx
        emotion = tone_detector.emotions[emotion_idx]

        print(f"Analysis #{analysis_id}: Detected emotion: {emotion['name']}")

        return jsonify({
            'status': 'success',
            'emotion': emotion['name'],
            'emoji': emotion['emoji'],
            'description': emotion['description'],
            'audio_file': 'simulated_recording.wav',
            'analysis_id': analysis_id,
            'is_speaking': is_speaking
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Keep the old endpoint for backward compatibility
@app.route('/record', methods=['POST'])
def record_audio():
    """Return a simulated response for backward compatibility"""
    try:
        # Return a random emotion
        import random
        emotion_idx = random.randint(0, len(tone_detector.emotions) - 1)
        emotion = tone_detector.emotions[emotion_idx]

        return jsonify({
            'status': 'success',
            'emotion': emotion['name'],
            'emoji': emotion['emoji'],
            'description': emotion['description'],
            'audio_file': 'simulated_recording.wav'
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# This is for local development
if __name__ == '__main__':
    app.run(debug=True)

# For Vercel deployment
app.debug = False