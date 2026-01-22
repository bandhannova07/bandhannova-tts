/**
 * TTS Generator - Frontend JavaScript
 */

// State Management
const state = {
    selectedLanguage: 'en',
    languages: {},
    currentAudio: null,
    isGenerating: false
};

// DOM Elements
const elements = {
    languageGrid: document.getElementById('languageGrid'),
    textInput: document.getElementById('textInput'),
    charCount: document.getElementById('charCount'),
    speedControl: document.getElementById('speedControl'),
    speedValue: document.getElementById('speedValue'),
    pitchControl: document.getElementById('pitchControl'),
    pitchValue: document.getElementById('pitchValue'),
    generateBtn: document.getElementById('generateBtn'),
    loadingState: document.getElementById('loadingState'),
    audioPlayer: document.getElementById('audioPlayer'),
    audioElement: document.getElementById('audioElement'),
    downloadBtn: document.getElementById('downloadBtn'),
    errorMessage: document.getElementById('errorMessage'),
    errorText: document.getElementById('errorText'),
    audioLanguage: document.getElementById('audioLanguage'),
    audioDuration: document.getElementById('audioDuration'),
    waveform: document.getElementById('waveform')
};

// Initialize App
async function init() {
    console.log('Initializing TTS Generator...');
    
    // Load languages
    await loadLanguages();
    
    // Setup event listeners
    setupEventListeners();
    
    // Check server health
    await checkHealth();
}

// Load Available Languages
async function loadLanguages() {
    try {
        const response = await fetch('/api/languages');
        const data = await response.json();
        
        if (data.success) {
            state.languages = data.languages;
            renderLanguages();
        } else {
            showError('Failed to load languages');
        }
    } catch (error) {
        console.error('Error loading languages:', error);
        showError('Failed to connect to server');
    }
}

// Render Language Options
function renderLanguages() {
    elements.languageGrid.innerHTML = '';
    
    Object.entries(state.languages).forEach(([code, lang]) => {
        const option = document.createElement('div');
        option.className = 'language-option';
        if (code === state.selectedLanguage) {
            option.classList.add('active');
        }
        
        option.innerHTML = `
            <span class="language-flag">${lang.flag}</span>
            <div class="language-name">${lang.name}</div>
            <div class="language-code">${code.toUpperCase()}</div>
        `;
        
        option.addEventListener('click', () => selectLanguage(code));
        elements.languageGrid.appendChild(option);
    });
}

// Select Language
function selectLanguage(code) {
    state.selectedLanguage = code;
    renderLanguages();
}

// Setup Event Listeners
function setupEventListeners() {
    // Text input character counter
    elements.textInput.addEventListener('input', updateCharCount);
    
    // Speed control
    elements.speedControl.addEventListener('input', (e) => {
        elements.speedValue.textContent = `${parseFloat(e.target.value).toFixed(1)}x`;
    });
    
    // Pitch control
    elements.pitchControl.addEventListener('input', (e) => {
        elements.pitchValue.textContent = e.target.value;
    });
    
    // Generate button
    elements.generateBtn.addEventListener('click', generateSpeech);
    
    // Download button
    elements.downloadBtn.addEventListener('click', downloadAudio);
    
    // Audio player events
    elements.audioElement.addEventListener('loadedmetadata', updateAudioInfo);
    elements.audioElement.addEventListener('play', drawWaveform);
}

// Update Character Count
function updateCharCount() {
    const count = elements.textInput.value.length;
    elements.charCount.textContent = count;
    
    if (count > 5000) {
        elements.charCount.style.color = 'var(--error)';
    } else {
        elements.charCount.style.color = 'var(--text-muted)';
    }
}

// Generate Speech
async function generateSpeech() {
    const text = elements.textInput.value.trim();
    
    // Validation
    if (!text) {
        showError('Please enter some text');
        return;
    }
    
    if (text.length > 5000) {
        showError('Text is too long. Maximum 5000 characters allowed');
        return;
    }
    
    // Disable button and show loading
    state.isGenerating = true;
    elements.generateBtn.disabled = true;
    elements.loadingState.classList.remove('hidden');
    elements.audioPlayer.classList.add('hidden');
    elements.errorMessage.classList.add('hidden');
    
    try {
        const speed = parseFloat(elements.speedControl.value);
        const pitch = parseInt(elements.pitchControl.value);
        
        console.log('Generating speech:', {
            language: state.selectedLanguage,
            textLength: text.length,
            speed,
            pitch
        });
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                language: state.selectedLanguage,
                speed: speed,
                pitch: pitch
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to generate speech');
        }
        
        // Get audio blob
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // Update audio player
        elements.audioElement.src = audioUrl;
        state.currentAudio = audioUrl;
        
        // Show audio player
        elements.audioPlayer.classList.remove('hidden');
        elements.loadingState.classList.add('hidden');
        
        // Auto play
        elements.audioElement.play();
        
        console.log('Speech generated successfully');
        
    } catch (error) {
        console.error('Error generating speech:', error);
        showError(error.message || 'Failed to generate speech');
        elements.loadingState.classList.add('hidden');
    } finally {
        state.isGenerating = false;
        elements.generateBtn.disabled = false;
    }
}

// Download Audio
function downloadAudio() {
    if (!state.currentAudio) return;
    
    const a = document.createElement('a');
    a.href = state.currentAudio;
    a.download = `tts_${state.selectedLanguage}_${Date.now()}.mp3`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Update Audio Info
function updateAudioInfo() {
    const duration = elements.audioElement.duration;
    const minutes = Math.floor(duration / 60);
    const seconds = Math.floor(duration % 60);
    
    elements.audioDuration.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    elements.audioLanguage.textContent = state.languages[state.selectedLanguage]?.name || state.selectedLanguage;
}

// Draw Waveform Visualization
function drawWaveform() {
    const canvas = elements.waveform;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = 100;
    
    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
    gradient.addColorStop(0, '#667eea');
    gradient.addColorStop(1, '#764ba2');
    
    // Draw animated waveform
    let x = 0;
    const draw = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        ctx.moveTo(0, canvas.height / 2);
        
        for (let i = 0; i < canvas.width; i++) {
            const y = canvas.height / 2 + Math.sin((i + x) * 0.05) * 20 * Math.random();
            ctx.lineTo(i, y);
        }
        
        ctx.strokeStyle = gradient;
        ctx.lineWidth = 2;
        ctx.stroke();
        
        x += 2;
        
        if (!elements.audioElement.paused) {
            requestAnimationFrame(draw);
        }
    };
    
    draw();
}

// Show Error Message
function showError(message) {
    elements.errorText.textContent = message;
    elements.errorMessage.classList.remove('hidden');
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        elements.errorMessage.classList.add('hidden');
    }, 5000);
}

// Check Server Health
async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        console.log('Server health:', data);
    } catch (error) {
        console.error('Server health check failed:', error);
        showError('Warning: Server connection unstable');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
