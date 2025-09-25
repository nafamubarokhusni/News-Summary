// DOM elements
const summaryForm = document.getElementById('summaryForm');
const urlInput = document.getElementById('urlInput');
const submitBtn = document.getElementById('submitBtn');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const resultSection = document.getElementById('resultSection');
const articleTitle = document.getElementById('articleTitle');
const articleUrl = document.getElementById('articleUrl');
const summaryText = document.getElementById('summaryText');

// Form submission handler
summaryForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const url = urlInput.value.trim();
    if (!url) {
        showError('Please enter a valid URL');
        return;
    }
    
    await summarizeArticle(url);
});

// Main function to summarize article
async function summarizeArticle(url) {
    try {
        // Show loading state
        showLoading();
        hideError();
        hideResult();
        
        // Make API request
        const response = await fetch('/api/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to summarize article');
        }
        
        // Show results
        displayResult(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while processing the article');
    } finally {
        hideLoading();
    }
}

// Display result
function displayResult(data) {
    articleTitle.textContent = data.title;
    articleUrl.href = data.url;
    summaryText.textContent = data.summary;
    
    showResult();
}

// UI helper functions
function showLoading() {
    loading.style.display = 'block';
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
}

function hideLoading() {
    loading.style.display = 'none';
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="fas fa-magic"></i> Summarize';
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function showResult() {
    resultSection.style.display = 'block';
    // Smooth scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function hideResult() {
    resultSection.style.display = 'none';
}

// Copy to clipboard function
async function copyToClipboard() {
    try {
        const text = summaryText.textContent;
        await navigator.clipboard.writeText(text);
        
        // Show feedback
        const copyBtn = document.querySelector('.action-btn:not(.secondary)');
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        copyBtn.style.background = '#48bb78';
        
        setTimeout(() => {
            copyBtn.innerHTML = originalText;
            copyBtn.style.background = '#667eea';
        }, 2000);
        
    } catch (error) {
        console.error('Failed to copy text:', error);
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = summaryText.textContent;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            alert('Summary copied to clipboard!');
        } catch (err) {
            alert('Failed to copy text. Please select and copy manually.');
        }
        
        document.body.removeChild(textArea);
    }
}

// Reset form function
function resetForm() {
    urlInput.value = '';
    hideResult();
    hideError();
    hideLoading();
    urlInput.focus();
}

// Auto-focus on input when page loads
document.addEventListener('DOMContentLoaded', () => {
    urlInput.focus();
});

// Handle URL validation
urlInput.addEventListener('input', (e) => {
    const url = e.target.value.trim();
    if (url && !isValidUrl(url)) {
        urlInput.setCustomValidity('Please enter a valid URL starting with http:// or https://');
    } else {
        urlInput.setCustomValidity('');
    }
});

// URL validation helper
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

// Handle paste event
urlInput.addEventListener('paste', (e) => {
    // Small delay to allow paste to complete
    setTimeout(() => {
        const pastedUrl = urlInput.value.trim();
        if (pastedUrl && isValidUrl(pastedUrl)) {
            // Auto-submit after paste if URL is valid
            setTimeout(() => {
                if (urlInput.value.trim() === pastedUrl) {
                    summaryForm.dispatchEvent(new Event('submit'));
                }
            }, 500);
        }
    }, 10);
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to submit
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        summaryForm.dispatchEvent(new Event('submit'));
    }
    
    // Escape to reset
    if (e.key === 'Escape') {
        resetForm();
    }
});

// Demo functionality
async function loadDemo() {
    try {
        showLoading();
        hideError();
        hideResult();
        
        // Fetch demo article data
        const response = await fetch('/api/demo');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error('Failed to load demo data');
        }
        
        // Generate summary using the same summarizer
        const summaryResponse = await fetch('/api/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: 'demo://sample-article' })
        });
        
        if (summaryResponse.ok) {
            const summaryData = await summaryResponse.json();
            displayResult(summaryData);
        } else {
            // Fallback: show the demo data with a simple summary
            const summary = data.content.split('. ').slice(0, 3).join('. ') + '.';
            displayResult({
                title: data.title,
                summary: summary,
                url: data.url
            });
        }
        
    } catch (error) {
        console.error('Demo error:', error);
        showError('Failed to load demo. Please try again.');
    } finally {
        hideLoading();
    }
}