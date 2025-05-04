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

    // Speech recognition variables
    let recognition = null;
    let transcriptBuffer = [];
    let currentTranscript = "";

    // Track detected emotions for overall summary
    let detectedEmotions = {};
    let totalDetections = 0;
    let detectedTexts = {}; // Store example texts for each detected emotion

    // Example texts for each emotion
    const exampleTexts = {
        "Formal": ["I hereby request your attention to this matter of utmost importance.",
                  "As per our previous correspondence, I would like to inform you of the following developments."],
        "Informal": ["Hey, what's up? Just checking in to see how you're doing.",
                    "So anyway, I was thinking we could grab lunch sometime?"],
        "Friendly": ["It's so wonderful to see you again! I've missed our chats.",
                    "I really appreciate your help with this project, you're amazing!"],
        "Aggressive": ["I've told you repeatedly to stop doing that! Listen to me!",
                      "This is completely unacceptable and I demand immediate action!"],
        "Optimistic": ["I'm sure we'll find a solution! Things are looking up!",
                      "This is going to be a great opportunity for all of us!"],
        "Informative": ["Studies show that regular exercise improves cognitive function.",
                       "The data indicates a 15% increase in productivity following the implementation."],
        "Entertaining": ["You won't believe what happened next! It was absolutely wild!",
                        "So there I was, standing in line, when suddenly..."],
        "Professional": ["Based on our analysis, we recommend proceeding with option B.",
                        "I've prepared a detailed report outlining our quarterly performance."],
        "Authoritative": ["As the expert in this field, I can assure you this is the correct approach.",
                         "My extensive experience in this area leads me to conclude that..."],
        "Animated": ["Oh my gosh! That's AMAZING! I can't believe it! Wow!",
                    "This is SO exciting! I'm absolutely thrilled about this news!"],
        "Humorous": ["So a penguin walks into a bar... you're going to love this!",
                    "My cooking is so bad, the smoke alarm cheers me on when I enter the kitchen!"],
        "Conversational": ["So anyway, I was thinking about what you said earlier...",
                          "That reminds me of something that happened last weekend."],
        "Directive": ["First, open the file. Then, click on settings. Finally, save changes.",
                     "Please ensure all documents are submitted by Friday at the latest."],
        "Assertive": ["I need this completed by Friday. No exceptions.",
                     "I believe this approach will yield the best results for our team."],
        "Questioning": ["Have you considered what might happen if we try a different approach?",
                       "What do you think would be the implications of this decision?"],
        "Empathic": ["I understand how difficult this must be for you. I'm here to help.",
                    "That sounds really challenging. How are you feeling about it?"],
        "Persuasive": ["Imagine how much better your life will be once you make this change.",
                      "You don't want to miss out on this incredible opportunity."]
    };

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
            // Remove overall summary styling when starting a new recording
            document.querySelector('.tone-display').classList.remove('overall-summary');
            // Hide detected text container when starting recording
            document.getElementById('detected-text-container').classList.add('hidden');
        } else {
            recordBtn.classList.remove('recording');
            btnText.textContent = 'Start Recording';
            timer.classList.add('hidden');
            seconds.textContent = '0';
            // Note: We don't reset the emotion display here anymore
            // This allows the overall summary to remain visible
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

                // Track emotions for summary
                if (data.emotion) {
                    totalDetections++;
                    if (detectedEmotions[data.emotion]) {
                        detectedEmotions[data.emotion]++;
                    } else {
                        detectedEmotions[data.emotion] = 1;
                    }

                    // Store a random example text for this emotion
                    if (exampleTexts[data.emotion] && exampleTexts[data.emotion].length > 0) {
                        const randomIndex = Math.floor(Math.random() * exampleTexts[data.emotion].length);
                        detectedTexts[data.emotion] = exampleTexts[data.emotion][randomIndex];
                    }
                }

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

    // Initialize speech recognition
    function initSpeechRecognition() {
        // Check if browser supports speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            console.error("Speech recognition not supported in this browser");
            statusMessage.textContent = "Speech-to-text not supported in your browser";
            return false;
        }

        // Create recognition object
        recognition = new SpeechRecognition();

        // Configure recognition
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        // Set up event handlers
        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            // Process results
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;

                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                    // Add to transcript buffer (keep last 5 sentences)
                    transcriptBuffer.push(transcript.trim());
                    if (transcriptBuffer.length > 5) {
                        transcriptBuffer.shift();
                    }
                } else {
                    interimTranscript += transcript;
                }
            }

            // Update current transcript with final + interim
            currentTranscript = finalTranscript + interimTranscript;

            // Update UI with detected text if speaking
            if (isSpeaking && currentTranscript.trim() !== '') {
                const detectedTextContainer = document.getElementById('detected-text-container');
                const detectedTextElement = document.getElementById('detected-text');

                detectedTextElement.textContent = `"${currentTranscript.trim()}"`;
                detectedTextContainer.classList.remove('hidden');
            }
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (event.error === 'no-speech') {
                // This is a common error, no need to show to user
                return;
            }
            statusMessage.textContent = `Speech recognition error: ${event.error}`;
        };

        recognition.onend = () => {
            // Restart recognition if recording is still active
            if (isRecording) {
                recognition.start();
            }
        };

        return true;
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

            // Initialize and start speech recognition
            if (initSpeechRecognition()) {
                try {
                    recognition.start();
                    console.log("Speech recognition started");
                } catch (e) {
                    console.error("Error starting speech recognition:", e);
                }
            }

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

        // Stop speech recognition
        if (recognition) {
            try {
                recognition.stop();
                console.log("Speech recognition stopped");
            } catch (e) {
                console.error("Error stopping speech recognition:", e);
            }
        }

        // Clear all intervals
        clearInterval(timerInterval);
        clearInterval(analysisInterval);
        clearInterval(speechDetectionInterval);

        // Reset state
        isRecording = false;
        isSpeaking = false;

        // Generate overall tone summary
        if (totalDetections > 0) {
            // Find the most frequent emotion
            let dominantEmotion = '';
            let maxCount = 0;

            for (const emotion in detectedEmotions) {
                if (detectedEmotions[emotion] > maxCount) {
                    maxCount = detectedEmotions[emotion];
                    dominantEmotion = emotion;
                }
            }

            // Calculate percentage
            const percentage = Math.round((maxCount / totalDetections) * 100);

            // Get the emoji for the dominant emotion
            let dominantEmoji = '😶';
            // We'll use the current emoji if it matches the dominant emotion
            if (emotionText.textContent.includes(dominantEmotion)) {
                dominantEmoji = emoji.textContent;
            }

            // Update UI with summary
            document.querySelector('.tone-display').classList.add('overall-summary');
            emoji.textContent = dominantEmoji;
            emotionText.textContent = `Overall Tone: ${dominantEmotion}`;
            descriptionText.textContent = `You spoke in a ${dominantEmotion.toLowerCase()} tone ${percentage}% of the time.`;
            statusMessage.textContent = `Recording stopped. Analyzed ${totalDetections} speech segments.`;

            // Display detected text
            const detectedTextContainer = document.getElementById('detected-text-container');
            const detectedTextElement = document.getElementById('detected-text');

            // Use the transcript buffer if we have actual transcribed text
            if (transcriptBuffer.length > 0) {
                // Join the last few transcripts, but limit to a reasonable length
                let displayText = transcriptBuffer.join(' ');
                if (displayText.length > 150) {
                    displayText = displayText.substring(displayText.length - 150);
                    // Try to start at a word boundary
                    const firstSpaceIndex = displayText.indexOf(' ');
                    if (firstSpaceIndex > 0) {
                        displayText = displayText.substring(firstSpaceIndex + 1);
                    }
                }
                detectedTextElement.textContent = `"${displayText}"`;
                detectedTextContainer.classList.remove('hidden');
            }
            // Fallback to example texts if no transcription is available
            else if (detectedTexts[dominantEmotion]) {
                detectedTextElement.textContent = `"${detectedTexts[dominantEmotion]}" (Example)`;
                detectedTextContainer.classList.remove('hidden');
            } else if (exampleTexts[dominantEmotion] && exampleTexts[dominantEmotion].length > 0) {
                // Fallback to a random example if we don't have a detected text
                const randomIndex = Math.floor(Math.random() * exampleTexts[dominantEmotion].length);
                detectedTextElement.textContent = `"${exampleTexts[dominantEmotion][randomIndex]}" (Example)`;
                detectedTextContainer.classList.remove('hidden');
            } else {
                detectedTextContainer.classList.add('hidden');
            }
        } else {
            // No speech was detected
            emoji.textContent = '😶';
            emotionText.textContent = 'No speech detected';
            descriptionText.textContent = 'Please try again and speak clearly.';
            statusMessage.textContent = 'Recording stopped';
        }

        updateUI(false);

        // Reset emotion tracking for next recording
        detectedEmotions = {};
        detectedTexts = {};
        totalDetections = 0;

        // Reset transcript data
        transcriptBuffer = [];
        currentTranscript = "";
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