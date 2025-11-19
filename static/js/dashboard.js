/**
 * Echo Universe - Dashboard JavaScript
 * Handles API interactions and UI updates
 */

// API base URL
const API_BASE = '';

// Toast notification helper
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => {
        toast.className = 'toast';
    }, 3000);
}

// Generic API call helper
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast(`Error: ${error.message}`, 'error');
        return { success: false, error: error.message };
    }
}

// Update connector status indicator
function updateStatusIndicator(connector, status) {
    const indicator = document.getElementById(`${connector}-status`);
    if (indicator) {
        indicator.textContent = status;
        indicator.className = 'status-indicator';

        if (status === 'connected') {
            indicator.classList.add('connected');
        } else if (status === 'error' || status === 'rate_limited') {
            indicator.classList.add('error');
        } else {
            indicator.classList.add('disconnected');
        }
    }
}

// Test a specific connector
async function testConnector(name) {
    showToast(`Testing ${name}...`, 'info');
    const result = await apiCall(`/api/test/${name}`);

    if (result.success) {
        updateStatusIndicator(name, 'connected');
        showToast(`${name} connected successfully!`, 'success');
    } else {
        updateStatusIndicator(name, 'error');
        showToast(`${name} connection failed: ${result.error}`, 'error');
    }

    return result;
}

// Test all connectors
async function testAllConnectors() {
    showToast('Testing all connectors...', 'info');
    const result = await apiCall('/api/test-all');

    if (result.success) {
        Object.entries(result.results).forEach(([name, data]) => {
            updateStatusIndicator(name, data.success ? 'connected' : 'error');
        });
        showToast('All connector tests completed', 'success');
    }

    return result;
}

// Refresh status of all connectors
async function refreshStatus() {
    const result = await apiCall('/api/status');

    if (result.success) {
        Object.entries(result.connectors).forEach(([name, data]) => {
            updateStatusIndicator(name, data.status);
        });
    }
}

// Send AI message
async function sendAIMessage() {
    const provider = document.getElementById('ai-provider').value;
    const message = document.getElementById('ai-message').value;
    const responseArea = document.getElementById('ai-response');

    if (!message.trim()) {
        showToast('Please enter a message', 'error');
        return;
    }

    responseArea.textContent = 'Sending...';

    const result = await apiCall('/api/ai/chat', {
        method: 'POST',
        body: JSON.stringify({ provider, message })
    });

    if (result.success && result.data) {
        responseArea.textContent = result.data.content || JSON.stringify(result.data, null, 2);
        showToast('Response received', 'success');
    } else {
        responseArea.textContent = `Error: ${result.error}`;
        showToast('Failed to get AI response', 'error');
    }
}

// Load GitHub repositories
async function loadRepos() {
    const responseArea = document.getElementById('github-repos');
    responseArea.textContent = 'Loading...';

    const result = await apiCall('/api/github/repos');

    if (result.success && result.data) {
        const repos = result.data.slice(0, 10);
        let output = repos.map(repo =>
            `${repo.name}\n  ${repo.description || 'No description'}\n  Stars: ${repo.stars}`
        ).join('\n\n');

        responseArea.textContent = output || 'No repositories found';
        showToast('Repositories loaded', 'success');
    } else {
        responseArea.textContent = `Error: ${result.error}`;
        showToast('Failed to load repositories', 'error');
    }
}

// Trigger Zapier webhook
async function triggerZapier() {
    const payloadText = document.getElementById('zapier-payload').value;
    const responseArea = document.getElementById('zapier-response');

    let payload;
    try {
        payload = payloadText.trim() ? JSON.parse(payloadText) : {};
    } catch (e) {
        showToast('Invalid JSON payload', 'error');
        return;
    }

    responseArea.textContent = 'Triggering...';

    const result = await apiCall('/api/zapier/trigger', {
        method: 'POST',
        body: JSON.stringify({ payload })
    });

    if (result.success) {
        responseArea.textContent = 'Webhook triggered successfully!';
        showToast('Zapier webhook triggered', 'success');
    } else {
        responseArea.textContent = `Error: ${result.error}`;
        showToast('Failed to trigger webhook', 'error');
    }
}

// List open source APIs
async function listOpenSourceAPIs() {
    const responseArea = document.getElementById('opensource-response');
    responseArea.textContent = 'Loading...';

    const result = await apiCall('/api/opensource/list');

    if (result.success && result.data) {
        let output = result.data.map(api =>
            `${api.name}\n  URL: ${api.base_url}\n  Auth: ${api.auth_type}\n  ${api.description}`
        ).join('\n\n');

        responseArea.textContent = output;
        showToast('APIs listed', 'success');
    } else {
        responseArea.textContent = `Error: ${result.error}`;
    }
}

// Generate text with Ollama
async function ollamaGenerate() {
    const model = document.getElementById('ollama-model').value || 'llama2';
    const prompt = document.getElementById('ollama-prompt').value;
    const responseArea = document.getElementById('opensource-response');

    if (!prompt.trim()) {
        showToast('Please enter a prompt', 'error');
        return;
    }

    responseArea.textContent = 'Generating...';

    const result = await apiCall('/api/opensource/ollama', {
        method: 'POST',
        body: JSON.stringify({ model, prompt })
    });

    if (result.success && result.data) {
        responseArea.textContent = result.data.response || JSON.stringify(result.data, null, 2);
        showToast('Text generated', 'success');
    } else {
        responseArea.textContent = `Error: ${result.error}`;
        showToast('Generation failed', 'error');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Refresh status button
    document.getElementById('refresh-all').addEventListener('click', refreshStatus);

    // Test all button
    document.getElementById('test-all').addEventListener('click', testAllConnectors);

    // Initial status refresh
    refreshStatus();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to send AI message
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (document.activeElement.id === 'ai-message') {
            sendAIMessage();
        }
    }
});
