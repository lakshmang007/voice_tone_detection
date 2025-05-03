import numpy as np
import librosa
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class ToneDetector:
    def __init__(self):
        self.emotions = {
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
        self.model_path = os.path.join(os.path.dirname(__file__), 'tone_model.pkl')
        self.scaler_path = os.path.join(os.path.dirname(__file__), 'scaler.pkl')

        # Check if model exists, otherwise create a simple one
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
        else:
            # Create a simple model (this would normally be trained on real data)
            self.model = RandomForestClassifier(n_estimators=10)
            self.scaler = StandardScaler()
            self._create_dummy_model()

    def _create_dummy_model(self):
        """Create a simple dummy model for demonstration purposes"""
        # Generate random features for each emotion
        num_emotions = len(self.emotions)
        samples_per_emotion = 100
        total_samples = num_emotions * samples_per_emotion

        X = np.random.rand(total_samples, 10)  # 100 samples per emotion, 10 features
        y = np.repeat(np.arange(num_emotions), samples_per_emotion)

        # Scale the features
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)

        # Train the model
        self.model.fit(X_scaled, y)

        # Save the model and scaler
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)

    def extract_features(self, audio_data, sample_rate):
        """Extract audio features from the audio data"""
        # Extract various features
        features = []

        # MFCCs (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=13)
        features.append(np.mean(mfccs, axis=1))

        # Spectral centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)
        features.append(np.mean(spectral_centroid))

        # Spectral bandwidth
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)
        features.append(np.mean(spectral_bandwidth))

        # Zero crossing rate
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_data)
        features.append(np.mean(zero_crossing_rate))

        # Chroma features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sample_rate)
        features.append(np.mean(chroma))

        # Flatten and concatenate all features
        features_flat = np.concatenate([f.flatten() if isinstance(f, np.ndarray) else [f] for f in features])

        # If we have fewer than 10 features, pad with zeros
        if len(features_flat) < 10:
            features_flat = np.pad(features_flat, (0, 10 - len(features_flat)))
        # If we have more than 10 features, truncate
        elif len(features_flat) > 10:
            features_flat = features_flat[:10]

        return features_flat

    def predict_emotion(self, audio_data, sample_rate):
        """Predict the emotion from audio data"""
        # Extract features
        features = self.extract_features(audio_data, sample_rate)

        # Scale features
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # Predict emotion
        emotion_idx = self.model.predict(features_scaled)[0]

        # Return emotion name and emoji
        return self.emotions[emotion_idx]