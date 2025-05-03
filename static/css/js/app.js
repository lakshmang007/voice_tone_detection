document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const recordBtn = document.getElementById('record-btn');
    const btnText = recordBtn.querySelector('.btn-text');
    const emoji = document.getElementById('emoji');
    const emotionText = document.getElementById('emotion-text');
    const descriptionText = document.getElementById('description-text');
    const timer = document.getElementById('timer');
    const seconds = document.getElementById('seconds');
    const statusMessage = document.getElementById('status-message');

    // Variables
    let isRecording = false;
    let timerInterval;
    let analysisInterval;
    let speechDetectionInterval;
    let mediaRecorder;
    let audioChunks = [];
    let stream;
    let analysisCount = 0;
    let audioContext;
    let analyser;
    let isSpeaking = false;
    let silenceTimer = 0;
    let speechTimer = 0;

    // Speech detection thresholds
    const SPEECH_THRESHOLD = 15; // Adjust based on testing
    const SILENCE_THRESHOLD = 5; // Number of consecutive silent frames to consider silence
    const SPEECH_CONFIRMATION_THRESHOLD = 3; // Number of consecutive speech frames to confirm speech

    // Functions
    function updateUI(recording) {
        if (recording) {
            recordBtn.classList.add('recording');
            btnText.textContent = 'Stop Recording';
            timer.classList.remove('hidden');
            emoji.textContent = '🎙️';
            emotionText.textContent = 'Listening...';
            descriptionText.textContent = '';
            statusMessage.textContent = 'Continuous voice tone detection active';
        } else {
            recordBtn.classList.remove('recording');
            btnText.textContent = 'Start Recording';
            timer.classList.add('hidden');
            seconds.textContent = '0';
        }
    }

    function startTimer() {
        let count = 0;
        seconds.textContent = count;

        timerInterval = setInterval(() => {
            count++;
            seconds.textContent = count;
        }, 1000);
    }

    // Function to detect if user is speaking
    function detectSpeech() {
        if (!analyser) return false;

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyser.getByteFrequencyData(dataArray);

        // Calculate average volume level
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
            sum += dataArray[i];
        }
        const average = sum / bufferLength;

        // Update speech detection state
        if (average > SPEECH_THRESHOLD) {
            speechTimer++;
            silenceTimer = 0;
            if (speechTimer >= SPEECH_CONFIRMATION_THRESHOLD && !isSpeaking) {
                isSpeaking = true;
                statusMessage.textContent = 'Speech detected - analyzing tone...';
                return true;
            }
        } else {
            silenceTimer++;
            speechTimer = 0;
            if (silenceTimer >= SILENCE_THRESHOLD && isSpeaking) {
                isSpeaking = false;
                statusMessage.textContent = 'Waiting for speech...';
            }
        }

        return isSpeaking;
    }

    async function analyzeAudio() {
        if (!isRecording || !mediaRecorder) return;

        // Only analyze if speech is detected
        if (!detectSpeech()) {
            // If no speech detected, don't change the current emotion
            return;
        }

        // Stop current recording to get the data
        mediaRecorder.stop();

        // Start a new recording session immediately
        audioChunks = [];
        try {
            const options = { mimeType: 'audio/webm' };
            mediaRecorder = new MediaRecorder(stream, options);
        } catch (e) {
            mediaRecorder = new MediaRecorder(stream);
        }

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.start(100);

        // Increment analysis count
        analysisCount++;

        // Request tone analysis from server
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    analysisId: analysisCount,
                    isSpeaking: true
                })
            });

            const data = await response.json();

            if (data.status === 'success') {
                // Update UI with detected emotion
                emoji.textContent = data.emoji;
                emotionText.textContent = `Detected: ${data.emotion}`;
                descriptionText.textContent = data.description;

                // Add animation to the emoji
                emoji.style.animation = 'bounce 0.5s';
                setTimeout(() => {
                    emoji.style.animation = '';
                }, 500);
            }
        } catch (error) {
            console.error('Error during analysis:', error);
        }
    }

    async function startRecording() {
        try {
            // Request microphone access
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Set up audio context and analyzer for speech detection
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioContext.createMediaStreamSource(stream);
            analyser = audioContext.createAnalyser();
            analyser.fftSize = 256;
            source.connect(analyser);

            // Create media recorder with specific MIME type
            const options = { mimeType: 'audio/webm' };
            try {
                mediaRecorder = new MediaRecorder(stream, options);
            } catch (e) {
                console.error('MediaRecorder with specified options not supported, using default');
                mediaRecorder = new MediaRecorder(stream);
            }
            audioChunks = [];

            // Set up event handlers
            mediaRecorder.ondataavailable = (event) => {
                audioChunks.push(event.data);
            };

            // Start recording - request data every 100ms
            mediaRecorder.start(100);
            isRecording = true;
            updateUI(true);
            startTimer();

            // Reset speech detection variables
            isSpeaking = false;
            silenceTimer = 0;
            speechTimer = 0;

            // Show browser's microphone indicator
            statusMessage.textContent = 'Waiting for speech...';

            // Start continuous analysis and speech detection
            speechDetectionInterval = setInterval(() => {
                detectSpeech();
            }, 100); // Check for speech every 100ms

            analysisInterval = setInterval(analyzeAudio, 1000); // Analyze every second

        } catch (error) {
            console.error('Error accessing microphone:', error);
            statusMessage.textContent = `Error accessing microphone: ${error.message}`;
            emoji.textContent = '🚫';
            emotionText.textContent = 'Microphone access denied';
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }

        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        // Close audio context
        if (audioContext && audioContext.state !== 'closed') {
            audioContext.close();
        }

        // Clear all intervals
        clearInterval(timerInterval);
        clearInterval(analysisInterval);
        clearInterval(speechDetectionInterval);

        // Reset state
        isRecording = false;
        isSpeaking = false;

        // Update UI
        emoji.textContent = '😶';
        emotionText.textContent = 'Waiting for voice...';
        descriptionText.textContent = '';
        statusMessage.textContent = 'Recording stopped';
        updateUI(false);
    }

    // Event Listeners
    recordBtn.addEventListener('click', () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    });

    // Add some CSS for the bounce animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
            40% {transform: translateY(-20px);}
            60% {transform: translateY(-10px);}
        }
    `;
    document.head.appendChild(style);
});