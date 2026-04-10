// Global State
let currentTranscript = "";
let currentTitle = "";

// DOM Elements
const fetchBtn = document.getElementById('fetchBtn');
const videoUrlInput = document.getElementById('videoUrl');
const loading = document.getElementById('loading');
const resultsArea = document.getElementById('resultsArea');
const videoTitle = document.getElementById('videoTitle');
const outputContent = document.getElementById('outputContent');
const panelTitle = document.getElementById('panelTitle');

// --- API Service: Fetch Transcript ---
async function fetchTranscription(url) {
    try {
        const response = await fetch(`/api/transcript?url=${encodeURIComponent(url)}`);
        const data = await response.json();
        
        // Robust check for transcript existence
        if (!response.ok || data.error || !data.transcript) {
            const errorMsg = data.error || (data.transcript === null ? "YouTube Blocked extraction" : "Unknown Server Error");
            showManualInput(errorMsg);
            return null;
        }
        return data;
    } catch (err) {
        showManualInput("Network Error: " + err.message);
        return null;
    }
}

function showManualInput(reason) {
    resultsArea.classList.remove('hidden');
    videoTitle.innerText = "Automatic Extraction Blocked";
    currentTranscript = ""; // Reset state
    
    outputContent.innerHTML = `
        <div class="manual-fallback glass-card" style="border: 1px solid #ef4444; background: rgba(239, 68, 68, 0.05); padding: 1.5rem; border-radius: 1rem;">
            <p style="color: #fca5a5; margin-bottom: 1rem; font-weight: 600;">
                <i class="fas fa-exclamation-triangle"></i> Extraction Failed: ${reason}
            </p>
            <p style="font-size: 0.9rem; margin-bottom: 1rem; color: #94a3b8;">
                YouTube has blocked the server's IP. To continue, please copy the transcript from the video on YouTube and paste it here:
            </p>
            <textarea id="manualPaste" class="action-btn" style="width: 100%; height: 180px; background: rgba(0,0,0,0.4); color: white; margin-bottom: 1.2rem; padding: 1rem; border: 1px solid var(--glass-border); border-radius: 0.8rem; font-size: 0.9rem;" placeholder="Paste transcript text here..."></textarea>
            <button id="submitManual" class="primary-btn" style="width: 100%; padding: 1rem;">Process Manual Transcript</button>
        </div>
    `;
    
    document.getElementById('submitManual').addEventListener('click', () => {
        const text = document.getElementById('manualPaste').value.trim();
        if (text.length < 30) return alert('Please paste a meaningful transcript!');
        
        currentTranscript = text;
        currentTitle = "Manual Input Analysis";
        videoTitle.innerText = "Analysis Ready (Manual)";
        outputContent.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <i class="fas fa-check-circle" style="color: #22c55e; font-size: 3rem; margin-bottom: 1rem;"></i>
                <h3 style="margin-bottom: 0.5rem;">Transcript Received!</h3>
                <p style="color: var(--text-muted);">Now use the Llama 3 buttons on the left to generate Summary, Quizzes or Timestamps.</p>
            </div>
        `;
    });
}

// --- AI Service: Cloud AI (Groq Llama 3) ---
async function callAIService(action) {
    if (!currentTranscript) return alert('Please enter a URL first or paste a transcript manually!');
    
    loading.classList.remove('hidden');
    outputContent.innerText = "Llama 3 is crunching the data for you...";

    try {
        const response = await fetch('/api/ai_process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                transcript: currentTranscript,
                action: action,
                model_type: "Groq",
                model_version: "llama-3.3-70b-versatile"
            })
        });
        
        const data = await response.json();
        loading.classList.add('hidden');
        
        if (data.result) {
            outputContent.innerText = data.result;
            const titles = { 'summary': 'Llama 3 Summary', 'timestamp': 'AI Timestamps', 'quiz': 'Llama 3 Quiz' };
            panelTitle.innerText = titles[action] || "AI Analysis";
        } else {
            throw new Error(data.detail || "AI failed to respond. Check API keys.");
        }
    } catch (err) {
        loading.classList.add('hidden');
        alert('AI Service Unavailable: ' + err.message);
    }
}

// --- Local Browser Summarization ---
function summarizeTextJS(text, sentenceCount = 7) {
    if (!text) return "No text available.";
    const sentences = text.match(/[^\.!\?]+[\.!\?]+/g) || [text];
    const words = text.toLowerCase().match(/\w+/g);
    const wordFreq = {};
    const stopWords = new Set(['the', 'and', 'is', 'a', 'to', 'in', 'it', 'i', 'that', 'with', 'on', 'this', 'for', 'was', 'so', 'of', 'you', 'your', 'are']);

    if (!words) return "Text too short to summarize.";

    words.forEach(word => { if (!stopWords.has(word)) wordFreq[word] = (wordFreq[word] || 0) + 1; });
    const sentenceScores = sentences.map(sentence => {
        let score = 0;
        (sentence.toLowerCase().match(/\w+/g) || []).forEach(word => { if (wordFreq[word]) score += wordFreq[word]; });
        return { sentence, score };
    });

    const summary = sentenceScores
        .sort((a, b) => b.score - a.score)
        .slice(0, sentenceCount)
        .sort((a, b) => sentences.indexOf(a.sentence) - sentences.indexOf(b.sentence))
        .map(item => item.sentence.trim())
        .join(' ');

    return `✨ Local JS Summary (High Accuracy):\n\n${summary}\n\n[Analysed locally in browser without API keys]`;
}

// --- Event Listeners ---
fetchBtn.addEventListener('click', async () => {
    const url = videoUrlInput.value.trim();
    if (!url) return alert('Please enter a valid YouTube URL');

    loading.classList.remove('hidden');
    resultsArea.classList.add('hidden');

    const data = await fetchTranscription(url);
    loading.classList.add('hidden');

    if (data) {
        currentTranscript = data.transcript;
        currentTitle = data.title || "Unknown Video";
        videoTitle.innerText = currentTitle;
        outputContent.innerText = "Extraction Successful! Use the buttons on the left to analyze the content.";
        resultsArea.classList.remove('hidden');
        panelTitle.innerText = "Results Overview";
    }
});

document.getElementById('showSummary').addEventListener('click', () => {
    if (!currentTranscript) return alert('No transcript loaded.');
    panelTitle.innerText = "Quick JS Summary";
    outputContent.innerText = summarizeTextJS(currentTranscript, 8);
});

document.getElementById('showTranscript').addEventListener('click', () => {
    if (!currentTranscript) return alert('No transcript loaded.');
    panelTitle.innerText = "Full Transcript";
    outputContent.innerText = currentTranscript;
});

// AI Buttons
document.getElementById('geminiSummary').addEventListener('click', () => callAIService('summary'));
document.getElementById('geminiTimestamps').addEventListener('click', () => callAIService('timestamp'));
document.getElementById('geminiQuiz').addEventListener('click', () => callAIService('quiz'));

// Copy & Download
document.getElementById('copyBtn').addEventListener('click', () => {
    if (!outputContent.innerText || outputContent.innerText.length < 5) return;
    navigator.clipboard.writeText(outputContent.innerText);
    alert('Copied to clipboard!');
});

document.getElementById('downloadBtn').addEventListener('click', () => {
    if (!outputContent.innerText || outputContent.innerText.length < 5) return;
    const blob = new Blob([outputContent.innerText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `Analysis_${Date.now()}.txt`; a.click();
});
