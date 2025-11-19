/**
 * Echo Fact-Check - Frontend Application
 */

class EchoFactCheck {
    constructor() {
        this.apiBase = '/api';
        this.ws = null;
        this.isLive = false;
        this.mediaRecorder = null;
        this.audioChunks = [];

        this.init();
    }

    init() {
        // Tab navigation
        this.initTabs();

        // Text check
        document.getElementById('check-text-btn').addEventListener('click', () => this.checkText());

        // File upload
        this.initFileUpload();

        // Live streaming
        this.initLiveStream();

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.checkText();
            }
        });
    }

    // Tab Navigation
    initTabs() {
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.dataset.tab;

                // Update buttons
                tabBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Update panes
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.remove('active');
                });
                document.getElementById(`${tabId}-tab`).classList.add('active');
            });
        });
    }

    // Text Fact-Check
    async checkText() {
        const textInput = document.getElementById('text-input');
        const text = textInput.value.trim();

        if (!text) {
            this.showError('Please enter text to fact-check');
            return;
        }

        this.showLoading('Analyzing text...');

        try {
            const response = await fetch(`${this.apiBase}/factcheck/text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content_type: 'text',
                    text_content: text,
                }),
            });

            const result = await response.json();

            if (result.success) {
                this.displayResults(result.data);
            } else {
                this.showError(result.message || 'Fact-check failed');
            }
        } catch (error) {
            this.showError(`Error: ${error.message}`);
        }
    }

    // File Upload
    initFileUpload() {
        const uploadZone = document.getElementById('upload-zone');
        const fileInput = document.getElementById('file-input');
        const filePreview = document.getElementById('file-preview');
        const checkBtn = document.getElementById('check-file-btn');

        // Click to upload
        uploadZone.addEventListener('click', () => fileInput.click());

        // Drag and drop
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('drag-over');
        });

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('drag-over');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('drag-over');
            if (e.dataTransfer.files.length) {
                this.handleFileSelect(e.dataTransfer.files[0]);
            }
        });

        // File input change
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        // Remove file
        document.querySelector('.remove-file-btn').addEventListener('click', () => {
            this.selectedFile = null;
            fileInput.value = '';
            filePreview.classList.add('hidden');
            checkBtn.disabled = true;
        });

        // Check file button
        checkBtn.addEventListener('click', () => this.checkFile());
    }

    handleFileSelect(file) {
        this.selectedFile = file;

        const filePreview = document.getElementById('file-preview');
        const fileName = filePreview.querySelector('.file-name');

        fileName.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
        filePreview.classList.remove('hidden');
        document.getElementById('check-file-btn').disabled = false;
    }

    async checkFile() {
        if (!this.selectedFile) {
            this.showError('Please select a file');
            return;
        }

        this.showLoading(`Analyzing ${this.selectedFile.name}...`);

        const formData = new FormData();
        formData.append('file', this.selectedFile);

        try {
            const response = await fetch(`${this.apiBase}/factcheck/file`, {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (result.success) {
                this.displayResults(result.data);
            } else {
                this.showError(result.message || 'File analysis failed');
            }
        } catch (error) {
            this.showError(`Error: ${error.message}`);
        }
    }

    // Live Streaming
    initLiveStream() {
        const startBtn = document.getElementById('start-live-btn');
        const stopBtn = document.getElementById('stop-live-btn');

        startBtn.addEventListener('click', () => this.startLiveCheck());
        stopBtn.addEventListener('click', () => this.stopLiveCheck());
    }

    async startLiveCheck() {
        try {
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

            // Connect WebSocket
            const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}${this.apiBase}/ws/live`;
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                this.isLive = true;
                this.updateLiveStatus(true);
                this.startRecording(stream);
            };

            this.ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleWebSocketMessage(message);
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.showError('Connection error');
                this.stopLiveCheck();
            };

            this.ws.onclose = () => {
                this.stopLiveCheck();
            };

        } catch (error) {
            this.showError(`Microphone access denied: ${error.message}`);
        }
    }

    startRecording(stream) {
        this.mediaRecorder = new MediaRecorder(stream, {
            mimeType: 'audio/webm',
        });

        this.audioChunks = [];

        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.audioChunks.push(event.data);
            }
        };

        this.mediaRecorder.onstop = async () => {
            if (this.audioChunks.length > 0 && this.ws && this.ws.readyState === WebSocket.OPEN) {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                const base64 = await this.blobToBase64(audioBlob);

                this.ws.send(JSON.stringify({
                    type: 'audio',
                    data: base64,
                    format: 'webm',
                }));

                this.audioChunks = [];
            }

            // Continue recording if still live
            if (this.isLive) {
                this.mediaRecorder.start();
                setTimeout(() => {
                    if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                        this.mediaRecorder.stop();
                    }
                }, 5000); // Send every 5 seconds
            }
        };

        // Start recording
        this.mediaRecorder.start();
        setTimeout(() => {
            if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                this.mediaRecorder.stop();
            }
        }, 5000);
    }

    stopLiveCheck() {
        this.isLive = false;

        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
        }

        if (this.mediaRecorder && this.mediaRecorder.stream) {
            this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }

        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }

        this.updateLiveStatus(false);
    }

    updateLiveStatus(active) {
        const statusDot = document.querySelector('.status-dot');
        const statusText = document.querySelector('.status-text');
        const startBtn = document.getElementById('start-live-btn');
        const stopBtn = document.getElementById('stop-live-btn');

        if (active) {
            statusDot.classList.add('active');
            statusText.textContent = 'Live - Listening...';
            startBtn.classList.add('hidden');
            stopBtn.classList.remove('hidden');
        } else {
            statusDot.classList.remove('active');
            statusText.textContent = 'Ready to stream';
            startBtn.classList.remove('hidden');
            stopBtn.classList.add('hidden');
        }
    }

    handleWebSocketMessage(message) {
        const transcript = document.getElementById('live-transcript');

        switch (message.type) {
            case 'connected':
                transcript.innerHTML = '<p class="status-message">Connected to live fact-check service</p>';
                break;

            case 'status':
                // Update status
                break;

            case 'claim':
                this.addLiveClaim(message.claim);
                break;

            case 'result':
                this.displayLiveResult(message.result);
                break;

            case 'error':
                this.showError(message.message);
                break;
        }
    }

    addLiveClaim(claim) {
        const container = document.getElementById('results-container');
        const emptyState = container.querySelector('.empty-state');
        if (emptyState) {
            container.innerHTML = '';
        }

        const claimCard = this.createClaimCard(claim);
        container.insertBefore(claimCard, container.firstChild);
    }

    displayLiveResult(result) {
        const scoreElement = document.getElementById('overall-score');
        const scoreValue = scoreElement.querySelector('.score-value');

        if (result.overall_credibility !== null) {
            scoreValue.textContent = `${Math.round(result.overall_credibility * 100)}%`;
            scoreValue.style.color = this.getScoreColor(result.overall_credibility);
            scoreElement.classList.remove('hidden');
        }
    }

    // Display Results
    displayResults(data) {
        this.hideLoading();

        const container = document.getElementById('results-container');
        const scoreElement = document.getElementById('overall-score');
        const scoreValue = scoreElement.querySelector('.score-value');

        // Clear container
        container.innerHTML = '';

        // Show overall score
        if (data.overall_credibility !== null) {
            scoreValue.textContent = `${Math.round(data.overall_credibility * 100)}%`;
            scoreValue.style.color = this.getScoreColor(data.overall_credibility);
            scoreElement.classList.remove('hidden');
        } else {
            scoreElement.classList.add('hidden');
        }

        // Show summary
        if (data.summary) {
            const summary = document.createElement('div');
            summary.className = 'results-summary';
            summary.innerHTML = `
                <div class="summary-title">📊 Summary</div>
                <p>${data.summary}</p>
            `;
            container.appendChild(summary);
        }

        // Show claims
        if (data.claims && data.claims.length > 0) {
            data.claims.forEach(claim => {
                const card = this.createClaimCard(claim);
                container.appendChild(card);
            });
        } else if (!data.summary) {
            container.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">ℹ️</span>
                    <p>No verifiable claims found in the content</p>
                </div>
            `;
        }
    }

    createClaimCard(claim) {
        const card = document.createElement('div');
        const status = claim.verification_status || claim.status;
        card.className = `claim-card ${status}`;

        let content = `
            <div class="claim-header">
                <div class="claim-text">"${claim.original_text || claim.text}"</div>
                <span class="claim-badge ${status}">${this.formatStatus(status)}</span>
            </div>
        `;

        if (claim.explanation) {
            content += `<p class="claim-explanation">${claim.explanation}</p>`;
        }

        if (claim.corrected_info || claim.correction) {
            content += `
                <div class="claim-correction">
                    <strong>✓ Correct information:</strong> ${claim.corrected_info || claim.correction}
                </div>
            `;
        }

        const confidence = claim.confidence_score || claim.confidence;
        if (confidence !== undefined) {
            content += `<div class="claim-confidence">Confidence: ${Math.round(confidence * 100)}%</div>`;
        }

        card.innerHTML = content;
        return card;
    }

    // Utility Functions
    showLoading(message) {
        const container = document.getElementById('results-container');
        const loading = document.getElementById('loading-indicator');
        const loadingText = loading.querySelector('.loading-text');

        container.classList.add('hidden');
        loading.classList.remove('hidden');
        loadingText.textContent = message || 'Processing...';
    }

    hideLoading() {
        const container = document.getElementById('results-container');
        const loading = document.getElementById('loading-indicator');

        loading.classList.add('hidden');
        container.classList.remove('hidden');
    }

    showError(message) {
        this.hideLoading();

        const container = document.getElementById('results-container');
        container.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">❌</span>
                <p style="color: var(--danger);">${message}</p>
            </div>
        `;
    }

    formatStatus(status) {
        const statusMap = {
            'true': 'TRUE',
            'false': 'FALSE',
            'partially_true': 'PARTIALLY TRUE',
            'misleading': 'MISLEADING',
            'unverifiable': 'UNVERIFIABLE',
            'opinion': 'OPINION',
            'satire': 'SATIRE',
        };
        return statusMap[status] || status.toUpperCase();
    }

    getScoreColor(score) {
        if (score >= 0.8) return 'var(--success)';
        if (score >= 0.6) return 'var(--info)';
        if (score >= 0.4) return 'var(--warning)';
        return 'var(--danger)';
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    async blobToBase64(blob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    window.echoApp = new EchoFactCheck();
});
