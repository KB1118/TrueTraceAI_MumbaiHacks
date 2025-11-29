// popup.js - Handles popup interactions

// Update log count on load
document.addEventListener('DOMContentLoaded', () => {
    updateLogCount();
});

// Update the log count display
function updateLogCount() {
    chrome.runtime.sendMessage({ type: "GET_LOGS" }, (response) => {
        if (response && response.logs) {
            document.getElementById('log-count').textContent = response.logs.length;
        }
    });
}

// Download log button
document.getElementById('download-log').addEventListener('click', () => {
    chrome.runtime.sendMessage({ type: "GET_LOGS" }, (response) => {
        if (response && response.logs) {
            if (response.logs.length === 0) {
                alert('No logs to download yet. Start checking some text first!');
                return;
            }

            // Use chrome.downloads API for better reliability
            const logData = JSON.stringify(response.logs, null, 2);
            const blob = new Blob([logData], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            chrome.downloads.download({
                url: url,
                filename: `truetrace_log_${new Date().toISOString().split('T')[0]}.json`,
                saveAs: true
            }, (downloadId) => {
                if (chrome.runtime.lastError) {
                    console.error('Download error:', chrome.runtime.lastError);
                    // Fallback to direct download
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `truetrace_log_${new Date().toISOString().split('T')[0]}.json`;
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                } else {
                    console.log('Download started with ID:', downloadId);
                }
                // Clean up after a delay
                setTimeout(() => URL.revokeObjectURL(url), 1000);
            });
        }
    });
});

// Clear log button
document.getElementById('clear-log').addEventListener('click', () => {
    if (confirm('Are you sure you want to clear all logs?')) {
        chrome.runtime.sendMessage({ type: "CLEAR_LOGS" }, (response) => {
            if (response && response.success) {
                updateLogCount();
                alert('Logs cleared successfully!');
            }
        });
    }
});