const API_BASE = 'http://localhost:3001/api';

async function checkHealth() {
    const statusDiv = document.getElementById('status');
    try {
        const response = await fetch('http://localhost:3001/health');
        const data = await response.json();
        statusDiv.innerHTML = '<div class="status success">✅ Server is running! Status: ' + data.status + '</div>';
    } catch (error) {
        statusDiv.innerHTML = '<div class="status error">❌ Server is not running. Please start the backend server.</div>';
    }
}

async function createAndRunTest() {
    const resultsDiv = document.getElementById('results');
    const statusDiv = document.getElementById('status');
    
    const testData = {
        name: document.getElementById('testName').value,
        description: 'Demo test created from simple interface',
        targetUrl: document.getElementById('targetUrl').value,
        commands: document.getElementById('commands').value.split('\n').filter(cmd => cmd.trim())
    };

    if (!testData.name || !testData.targetUrl || testData.commands.length === 0) {
        statusDiv.innerHTML = '<div class="status error">❌ Please fill in all fields</div>';
        return;
    }

    try {
        statusDiv.innerHTML = '<div class="status">🔄 Creating test...</div>';
        
        // Create test
        const createResponse = await fetch(`${API_BASE}/tests/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testData)
        });
        
        if (!createResponse.ok) {
            const errorData = await createResponse.json().catch(() => ({ error: createResponse.statusText }));
            throw new Error(`Failed to create test: ${errorData.error || createResponse.statusText}`);
        }
        
        const testSession = await createResponse.json();
        statusDiv.innerHTML = '<div class="status success">✅ Test created! Session ID: ' + testSession.sessionId + '</div>';
        
        // Execute test
        statusDiv.innerHTML = '<div class="status">🚀 Executing test...</div>';
        const executeResponse = await fetch(`${API_BASE}/tests/execute/${testSession.sessionId}`, {
            method: 'POST'
        });
        
        if (!executeResponse.ok) {
            const errorData = await executeResponse.json().catch(() => ({ error: executeResponse.statusText }));
            throw new Error(`Failed to execute test: ${errorData.error || executeResponse.statusText}`);
        }
        
        const results = await executeResponse.json();
        statusDiv.innerHTML = '<div class="status success">✅ Test completed!</div>';
        
        // Display results
        displayResults(results);
        
    } catch (error) {
        statusDiv.innerHTML = '<div class="status error">❌ Error: ' + error.message + '</div>';
        console.error('Test execution error:', error);
    }
}

function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    
    let resultsHtml = '<div class="test-result">';
    resultsHtml += `<h3>Test Results</h3>`;
    resultsHtml += `<p><strong>Status:</strong> ${results.status}</p>`;
    resultsHtml += `<p><strong>Summary:</strong> ${results.summary.passed}/${results.summary.total} steps passed</p>`;
    
    if (results.summary.failed > 0) {
        resultsHtml += `<p><strong>Failed:</strong> ${results.summary.failed} steps</p>`;
    }
    
    resultsHtml += '<h4>Steps:</h4><ul>';
    
    results.results.forEach((result, index) => {
        const status = result.status === 'passed' ? '✅' : '❌';
        resultsHtml += `<li>${status} Step ${index + 1}: ${result.status}`;
        if (result.error) {
            resultsHtml += ` - <span style="color: #f44336;">${result.error}</span>`;
        }
        if (result.actualResult) {
            resultsHtml += ` - <span style="color: #4CAF50;">${result.actualResult}</span>`;
        }
        resultsHtml += '</li>';
    });
    
    resultsHtml += '</ul>';
    
    // Add link to view detailed results
    resultsHtml += `<p><a href="/api/tests/${results.sessionId}" target="_blank">View detailed JSON results</a></p>`;
    
    resultsHtml += '</div>';
    resultsDiv.innerHTML = resultsHtml;
}

async function loadTestHistory() {
    try {
        const response = await fetch(`${API_BASE}/tests`);
        const sessions = await response.json();
        
        const historyDiv = document.getElementById('history');
        if (!historyDiv) return;
        
        if (sessions.length === 0) {
            historyDiv.innerHTML = '<p>No test history yet.</p>';
            return;
        }
        
        let historyHtml = '<h3>Recent Tests</h3><ul>';
        sessions.slice(0, 5).forEach(session => {
            const statusIcon = session.status === 'passed' ? '✅' : session.status === 'failed' ? '❌' : '⏳';
            historyHtml += `<li>${statusIcon} ${session.name} - ${session.status} (${new Date(session.created_at).toLocaleString()})</li>`;
        });
        historyHtml += '</ul>';
        
        historyDiv.innerHTML = historyHtml;
    } catch (error) {
        console.error('Failed to load test history:', error);
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Check server status on page load
    checkHealth();
    
    // Load test history if history div exists
    loadTestHistory();
    
    // Add event listeners to buttons
    const checkHealthBtn = document.getElementById('checkHealthBtn');
    const createTestBtn = document.getElementById('createTestBtn');
    
    if (checkHealthBtn) {
        checkHealthBtn.addEventListener('click', checkHealth);
    }
    
    if (createTestBtn) {
        createTestBtn.addEventListener('click', createAndRunTest);
    }
});
