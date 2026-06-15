document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('analyze-form');
    const textarea = document.getElementById('news-text');
    const charCount = document.querySelector('.char-count');
    const resultsCard = document.getElementById('results-card');
    const loader = document.getElementById('result-loader');
    const resultContent = document.getElementById('result-content');
    
    const predictionBadge = document.getElementById('prediction-badge');
    const confidencePercentage = document.getElementById('confidence-percentage');
    const confidenceBar = document.getElementById('confidence-bar');
    
    const reportBox = document.getElementById('report-box');
    const reportIcon = document.getElementById('report-icon');
    const reportTitle = document.getElementById('report-title');
    const reportDesc = document.getElementById('report-desc');
    const clearBtn = document.getElementById('clear-btn');
    
    // Character count update
    textarea.addEventListener('input', () => {
        const count = textarea.value.length;
        charCount.textContent = `${count.toLocaleString()} characters`;
    });

    // Clear form and reset results
    clearBtn.addEventListener('click', () => {
        textarea.value = '';
        charCount.textContent = '0 characters';
        resultsCard.classList.add('hidden');
        textarea.focus();
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const textValue = textarea.value.trim();
        
        if (!textValue) return;

        // Show results card, loader and hide old content
        resultsCard.classList.remove('hidden');
        loader.classList.remove('hidden');
        resultContent.classList.add('hidden');
        
        // Scroll results card into view smoothly
        resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: textValue })
            });

            const data = await response.json();
            
            if (data.status === 'success') {
                displayResult(data.prediction, data.confidence);
            } else {
                showError(data.message || 'An error occurred during prediction.');
            }
        } catch (error) {
            console.error('Error:', error);
            showError('Server connection failed. Make sure app.py is running.');
        }
    });

    function displayResult(prediction, confidence) {
        // Hide loader, show content
        loader.classList.add('hidden');
        resultContent.classList.remove('hidden');
        
        // Reset dynamic classes
        predictionBadge.className = 'badge';
        confidenceBar.className = 'gauge-bar-fill';
        reportBox.className = 'report-box';
        
        if (prediction === 'Real') {
            // Apply Real News styling
            predictionBadge.textContent = 'REAL NEWS';
            predictionBadge.classList.add('real');
            confidenceBar.classList.add('real');
            reportBox.classList.add('real');
            
            // Set SVG and texts
            setSvgIcon('real');
            reportTitle.textContent = 'High Integrity Verified';
            reportDesc.textContent = 'Linguistic and stylistic analysis suggests this article aligns with verified journalistic standards. It features structured syntax and lacks sensationalism.';
        } else {
            // Apply Fake News styling
            predictionBadge.textContent = 'MISLEADING / FAKE';
            predictionBadge.classList.add('fake');
            confidenceBar.classList.add('fake');
            reportBox.classList.add('fake');
            
            // Set SVG and texts
            setSvgIcon('fake');
            reportTitle.textContent = 'Misleading Indicators Detected';
            reportDesc.textContent = 'Warning: High correlation with clickbait phrasing, extreme sentiments, or unverified claims. We recommend cross-referencing this content with established sources.';
        }
        
        // Animate confidence bar and text
        confidenceBar.style.width = '0%';
        setTimeout(() => {
            confidenceBar.style.width = `${confidence}%`;
        }, 100);
        
        animatePercentage(confidence);
    }

    function showError(message) {
        loader.classList.add('hidden');
        resultContent.classList.remove('hidden');
        
        predictionBadge.className = 'badge fake';
        predictionBadge.textContent = 'ERROR';
        confidencePercentage.textContent = '0%';
        confidenceBar.className = 'gauge-bar-fill';
        confidenceBar.style.width = '0%';
        
        reportBox.className = 'report-box fake';
        setSvgIcon('error');
        reportTitle.textContent = 'Analysis Failed';
        reportDesc.textContent = message;
    }

    // Dynamic SVG injection
    function setSvgIcon(type) {
        reportIcon.innerHTML = '';
        if (type === 'real') {
            // Check-circle
            reportIcon.setAttribute('viewBox', '0 0 24 24');
            reportIcon.innerHTML = `
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline points="22 4 12 14.01 9 11.01" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            `;
        } else if (type === 'fake') {
            // Alert-triangle
            reportIcon.setAttribute('viewBox', '0 0 24 24');
            reportIcon.innerHTML = `
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="17" x2="12.01" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            `;
        } else {
            // Error cross
            reportIcon.setAttribute('viewBox', '0 0 24 24');
            reportIcon.innerHTML = `
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            `;
        }
    }

    // Number animation utility
    function animatePercentage(target) {
        let current = 0;
        const duration = 800; // ms
        const stepTime = 16; // ~60fps
        const increment = target / (duration / stepTime);
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                clearInterval(timer);
                confidencePercentage.textContent = `${target.toFixed(1)}%`;
            } else {
                confidencePercentage.textContent = `${current.toFixed(1)}%`;
            }
        }, stepTime);
    }
});
