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
        if (data.error) throw new Error(data.error);
        if (!response.ok) throw new Error('Failed to fetch transcript');
        return data;
    } catch (err) {
        console.error(err);
        alert(`Transcription Error: ${err.message}\nTip: Vercel IPs are sometimes blocked by YouTube. Try running locally or use a proxy.`);
        return null;
    }
}

// --- AI Service: Cloud AI (Now Exclusively Groq Llama 3) ---
async function callAIService(action) {
    if (!currentTranscript) return alert('Fetch a video first!');
    
    loading.classList.remove('hidden');
    outputContent.innerText = "Processing with Llama 3.3 Pro Engine...";

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
            throw new Error(data.detail || "AI response empty");
        }
    } catch (err) {
        loading.classList.add('hidden');
        alert('AI Error: ' + err.message);
        outputContent.innerText = "Error: " + err.message;
    }
}

// --- Local Browser Summarization ---
function summarizeTextJS(text, sentenceCount = 5) {
    if (!text) return "No text available.";
    const sentences = text.match(/[^\.!\?]+[\.!\?]+/g) || [text];
    const words = text.toLowerCase().match(/\w+/g);
    const wordFreq = {};
    const stopWords = new Set(['the', 'and', 'is', 'a', 'to', 'in', 'it', 'i', 'that', 'with', 'on', 'this', 'for', 'was', 'so', 'of']);

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

    return `✨ JS-Powered Summary:\n\n${summary}\n\n[Summarized locally in your browser]`;
}

// --- Event Listeners ---
fetchBtn.addEventListener('click', async () => {
    const url = videoUrlInput.value;
    if (!url) return alert('Please enter a URL');

    loading.classList.remove('hidden');
    resultsArea.classList.add('hidden');

    const data = await fetchTranscription(url);
    loading.classList.add('hidden');

    if (data) {
        currentTranscript = data.transcript;
        currentTitle = data.title;
        videoTitle.innerText = data.title;
        outputContent.innerText = "Video analyzed successfully! Use the buttons below.";
        resultsArea.classList.remove('hidden');
    }
});

document.getElementById('showSummary').addEventListener('click', () => {
    panelTitle.innerText = "Quick JS Summary";
    outputContent.innerText = summarizeTextJS(currentTranscript, 7);
});

document.getElementById('showTranscript').addEventListener('click', () => {
    panelTitle.innerText = "Full Transcript";
    outputContent.innerText = currentTranscript;
});

// AI Buttons
document.getElementById('geminiSummary').addEventListener('click', () => callAIService('summary'));
document.getElementById('geminiTimestamps').addEventListener('click', () => callAIService('timestamp'));
document.getElementById('geminiQuiz').addEventListener('click', () => callAIService('quiz'));

// Copy & Download
document.getElementById('copyBtn').addEventListener('click', () => {
    navigator.clipboard.writeText(outputContent.innerText);
    alert('Copied to clipboard!');
});

document.getElementById('downloadBtn').addEventListener('click', () => {
    const blob = new Blob([outputContent.innerText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = `${currentTitle}_summary.txt`; a.click();
});
