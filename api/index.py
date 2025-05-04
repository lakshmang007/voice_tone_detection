from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Voice Tone Detection</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
                color: #333;
            }
            h1 {
                color: #6c5ce7;
                text-align: center;
            }
            .container {
                background-color: #f9f9f9;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .emoji {
                font-size: 72px;
                text-align: center;
                margin: 20px 0;
            }
            .btn {
                display: inline-block;
                background-color: #6c5ce7;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                text-decoration: none;
                margin: 10px 0;
                text-align: center;
            }
            .btn:hover {
                background-color: #5649c0;
            }
            .social {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-top: 30px;
            }
            .social a {
                color: #6c5ce7;
                text-decoration: none;
                display: flex;
                align-items: center;
            }
            .social a:hover {
                text-decoration: underline;
            }
            footer {
                text-align: center;
                margin-top: 40px;
                color: #666;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <h1>Voice Tone Detection</h1>

        <div class="container">
            <div class="emoji">🎤</div>
            <h2>Welcome to Voice Tone Detection!</h2>
            <p>This application uses machine learning to detect the emotional tone in human voice and displays it as emojis.</p>
            <p>The application includes:</p>
            <ul>
                <li>Real-time voice tone detection</li>
                <li>17 different emotional tones</li>
                <li>Example sentences for each tone</li>
                <li>Continuous speech recognition</li>
            </ul>
            <p>The full interactive application is available on GitHub.</p>
            <div style="text-align: center;">
                <a href="https://github.com/lakshmang007/voice_tone_detection" class="btn">View on GitHub</a>
            </div>
        </div>

        <div class="social">
            <a href="https://github.com/lakshmang007/voice_tone_detection" target="_blank">
                <span style="font-size: 24px; margin-right: 5px;">&#128187;</span> GitHub
            </a>
            <a href="https://www.linkedin.com/in/lakshman-g-b1a5a0214" target="_blank">
                <span style="font-size: 24px; margin-right: 5px;">&#128101;</span> LinkedIn
            </a>
        </div>

        <footer>
            <p>Voice Tone Detection Project &copy; 2025</p>
        </footer>
    </body>
    </html>
    """

@app.route('/api/hello')
def hello():
    return jsonify({"message": "Hello from Voice Tone Detection API!"})

# This is for Vercel serverless functions
def handler(request, context):
    return app(request)

# This is for local development
if __name__ == '__main__':
    app.run(debug=True)
