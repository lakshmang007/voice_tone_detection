# Voice Tone Detection

A machine learning project that detects human voice tone and displays the emotional state as an emoji in a web interface.

## Features

- Real-time voice recording
- Emotion detection from voice
- Visual feedback with emojis
- Modern and responsive UI

## Emotions Detected

- 😐 Neutral
- 😊 Happy
- 😢 Sad
- 😠 Angry
- 😲 Surprised
- 😨 Fearful

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python main.py
```

2. Open your browser and navigate to `http://localhost:5000`
3. Click the "Start Recording" button and speak for 3 seconds
4. The system will analyze your voice and display the detected emotion

## Technical Details

- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, JavaScript
- **Machine Learning**: scikit-learn, librosa for audio feature extraction
- **Audio Processing**: sounddevice, scipy

## Project Structure

```
voice_tone_detection/
├── main.py                # Flask application
├── model/
│   └── tone_detector.py   # Emotion detection model
├── static/
│   └── css/
│       ├── style.css      # CSS styling
│       └── js/
│           └── app.js     # JavaScript functionality
└── templates/
    └── index.html         # HTML template
```

## Future Improvements

- Train the model on a larger dataset for better accuracy
- Add more emotions to detect
- Implement real-time streaming analysis
- Add history of detected emotions
- Support for multiple languages
