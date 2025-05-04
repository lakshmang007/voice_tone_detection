from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# Define emotions directly in the main file for simplicity
emotions = {
    0: {"name": "Formal", "emoji": "🧐", "description": "Clear, precise, and professional"},
    1: {"name": "Informal", "emoji": "😌", "description": "Conversational, relaxed, and friendly"},
    2: {"name": "Friendly", "emoji": "😊", "description": "Warm, approachable, and welcoming"},
    3: {"name": "Aggressive", "emoji": "😠", "description": "Loud, forceful, and confrontational"},
    4: {"name": "Optimistic", "emoji": "😃", "description": "Enthusiastic, positive, and upbeat"},
    5: {"name": "Informative", "emoji": "📚", "description": "Neutral, factual, and educational"},
    6: {"name": "Entertaining", "emoji": "🎭", "description": "Humorous, engaging, and captivating"},
    7: {"name": "Professional", "emoji": "👔", "description": "Confident, authoritative, and credible"},
    8: {"name": "Authoritative", "emoji": "👑", "description": "Confident, expert, and persuasive"},
    9: {"name": "Animated", "emoji": "✨", "description": "Energetic, lively, and enthusiastic"},
    10: {"name": "Humorous", "emoji": "😄", "description": "Playful, witty, and lighthearted"},
    11: {"name": "Conversational", "emoji": "💬", "description": "Natural, relatable, and engaging"},
    12: {"name": "Directive", "emoji": "👉", "description": "Clear, concise, and commanding"},
    13: {"name": "Assertive", "emoji": "💪", "description": "Confident, firm, and unapologetic"},
    14: {"name": "Questioning", "emoji": "🤔", "description": "Curious, open, and seeking information"},
    15: {"name": "Empathic", "emoji": "💖", "description": "Understanding, supportive, and compassionate"},
    16: {"name": "Persuasive", "emoji": "🎯", "description": "Motivating, encouraging, and influential"}
}

# Store the last emotion index
last_emotion_idx = 0

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
                emotion = emotions[app.last_emotion_idx]
            else:
                # Default to neutral if no previous emotion
                neutral_idx = next((i for i, e in emotions.items()
                                  if e['name'].lower() == 'formal'), 0)
                emotion = emotions[neutral_idx]

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
                emotion_idx = (app.last_emotion_idx + shift) % len(emotions)
            else:  # Random
                emotion_idx = random.randint(0, len(emotions) - 1)
        else:
            # First time, pick a random emotion
            emotion_idx = random.randint(0, len(emotions) - 1)

        # Store for next time
        app.last_emotion_idx = emotion_idx
        emotion = emotions[emotion_idx]

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
        emotion_idx = random.randint(0, len(emotions) - 1)
        emotion = emotions[emotion_idx]

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