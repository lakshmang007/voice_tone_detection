from flask import Flask, Response, request, jsonify
import random
import json

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

app = Flask(__name__)
last_emotion_idx = 0

# Simple HTML page for the root route
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Voice Tone Detector</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background-color: #f9f9f9;
            color: #2d3436;
        }
        h1 {
            color: #6c5ce7;
            text-align: center;
        }
        .message {
            background-color: #ffffff;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 2rem;
        }
        .emoji {
            font-size: 6rem;
            margin-bottom: 1rem;
        }
        .links {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
        }
        .link {
            display: inline-block;
            background-color: #6c5ce7;
            color: white;
            padding: 0.8rem 1.5rem;
            border-radius: 2rem;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .link:hover {
            background-color: #a29bfe;
            transform: translateY(-2px);
        }
        footer {
            text-align: center;
            margin-top: 2rem;
            color: #636e72;
            font-size: 0.9rem;
        }
        .social-links {
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 1rem;
        }
        .social-link {
            color: #6c5ce7;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            padding: 0.5rem 1rem;
            border-radius: 2rem;
            background-color: rgba(108, 92, 231, 0.1);
            display: flex;
            align-items: center;
        }
        .social-link:hover {
            background-color: rgba(108, 92, 231, 0.2);
            transform: translateY(-2px);
        }
        .social-icon {
            margin-right: 0.5rem;
            font-size: 1.2rem;
        }
    </style>
</head>
<body>
    <h1>Voice Tone Detector</h1>

    <div class="message">
        <div class="emoji">🎤</div>
        <h2>Welcome to Voice Tone Detection!</h2>
        <p>This application detects human voice tones and displays them as emojis.</p>
        <p>The full application with interactive features is available on GitHub.</p>

        <div class="links">
            <a href="https://github.com/lakshmang007/voice_tone_detection" class="link">View on GitHub</a>
        </div>
    </div>

    <footer>
        <p>Voice Tone Detection Project &copy; 2023</p>
        <div class="social-links">
            <a href="https://github.com/lakshmang007/voice_tone_detection" target="_blank" class="social-link">
                <span class="social-icon">&#128187;</span> GitHub
            </a>
            <a href="https://www.linkedin.com/in/lakshman-g-b1a5a0214" target="_blank" class="social-link">
                <span class="social-icon">&#128101;</span> LinkedIn
            </a>
        </div>
    </footer>
</body>
</html>
"""

def handle_request(request):
    """Handle HTTP request for Vercel serverless function"""
    # Handle root path
    if request.path == '/':
        return Response(HTML_CONTENT, mimetype='text/html')

    # Handle analyze endpoint
    if request.path == '/analyze' and request.method == 'POST':
        try:
            # Get request data
            analysis_id = None
            is_speaking = False

            if request.is_json:
                data = request.get_json()
                analysis_id = data.get('analysisId', 0)
                is_speaking = data.get('isSpeaking', False)

            # Return a random emotion
            emotion_idx = random.randint(0, len(emotions) - 1)
            emotion = emotions[emotion_idx]

            response_data = {
                'status': 'success',
                'emotion': emotion['name'],
                'emoji': emotion['emoji'],
                'description': emotion['description'],
                'audio_file': 'simulated_recording.wav',
                'analysis_id': analysis_id,
                'is_speaking': is_speaking
            }

            return Response(
                json.dumps(response_data),
                mimetype='application/json'
            )

        except Exception as e:
            error_response = {
                'status': 'error',
                'message': str(e)
            }
            return Response(
                json.dumps(error_response),
                status=500,
                mimetype='application/json'
            )

    # Handle record endpoint
    if request.path == '/record' and request.method == 'POST':
        try:
            # Return a random emotion
            emotion_idx = random.randint(0, len(emotions) - 1)
            emotion = emotions[emotion_idx]

            response_data = {
                'status': 'success',
                'emotion': emotion['name'],
                'emoji': emotion['emoji'],
                'description': emotion['description'],
                'audio_file': 'simulated_recording.wav'
            }

            return Response(
                json.dumps(response_data),
                mimetype='application/json'
            )

        except Exception as e:
            error_response = {
                'status': 'error',
                'message': str(e)
            }
            return Response(
                json.dumps(error_response),
                status=500,
                mimetype='application/json'
            )

    # Handle 404 for other routes
    return Response('Not Found', status=404)

# Vercel serverless function handler
def handler(req, context):
    with app.request_context(req.environ):
        return handle_request(request)

# This is for local development
if __name__ == '__main__':
    app.run(debug=True)
