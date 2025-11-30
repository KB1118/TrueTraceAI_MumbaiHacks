// 1. SET YOUR API KEY HERE FOR TESTING
// (Or create a config.js file with: const GEMINI_API_KEY = "...")
const FALLBACK_KEY = "YOUR_API_KEY_HERE"; 

// Try to import config.js, but don't crash if it's missing
try {
    importScripts("config.js");
} catch (e) {
    console.log("config.js not found. Using fallback key.");
}

// Log storage
let analysisLog = [];

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    if (msg.type === "CHECK_TEXT") {
        console.log("Received request to check text...");
        handleAnalysis(msg.payload, sendResponse, sender.tab.id);
        return true; // Keep channel open for async response
    } else if (msg.type === "GET_LOGS") {
        sendResponse({ logs: analysisLog });
        return true;
    } else if (msg.type === "CLEAR_LOGS") {
        analysisLog = [];
        sendResponse({ success: true });
        return true;
    }
});

// Helper function to send progress updates
function sendProgress(tabId, progress, status) {
    chrome.tabs.sendMessage(tabId, {
        type: "PROGRESS_UPDATE",
        progress: progress,
        status: status
    }).catch(() => {
        // Ignore errors if content script isn't ready
    });
}

async function handleAnalysis(text, sendResponse, tabId) {
    try {
        // Send initial progress
        sendProgress(tabId, 10, "Initializing...");
        
        // Determine which key to use
        let apiKey = null;
        if (typeof GEMINI_API_KEY !== 'undefined') apiKey = GEMINI_API_KEY;
        else if (typeof FALLBACK_KEY !== 'undefined' && FALLBACK_KEY !== "YOUR_API_KEY_HERE") apiKey = FALLBACK_KEY;

        if (!apiKey) {
            sendResponse({ error: "API Key missing. Please edit background.js and add your key." });
            return;
        }

        sendProgress(tabId, 20, "Preparing analysis...");

        const result = await analyzeText(text, apiKey, tabId);
        
        sendProgress(tabId, 90, "Finalizing...");
        
        // Log the result
        if (result.result) {
            const logEntry = {
                timestamp: new Date().toISOString(),
                text: text.substring(0, 200) + (text.length > 200 ? "..." : ""),
                analysis: result.result,
                truthScore: result.truthScore || "N/A"
            };
            analysisLog.push(logEntry);
            
            // Keep only last 100 entries
            if (analysisLog.length > 100) {
                analysisLog.shift();
            }
            
            // Optional: Download log automatically (commented out by default)
            // downloadLog();
        }
        
        sendProgress(tabId, 100, "Complete!");
        
        sendResponse(result);
    } catch (err) {
        sendResponse({ error: err.message });
    }
}

async function analyzeText(text, apiKey, tabId) {
    try {
        sendProgress(tabId, 30, "Connecting to Gemini...");
        
        const endpoint =
            `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${apiKey}`;

        const body = {
            contents: [
                {
                    role: "user",
                    parts: [
                        {
                            text: `
You are a fact-checking AI. Use the google_search tool to verify claims.
Always cite the sources you used.

Respond EXACTLY in this format:

**Truth Score: X/10**
[3-sentence analysis]
**Sources:**
1. Title - URL
2. Title - URL

Text:
"${text}"
                            `
                        }
                    ]
                }
            ],

            // ✓ FINAL CORRECT TOOL (no toolConfig)
            tools: [
                {
                    google_search: {}
                }
            ],

            generationConfig: {
                temperature: 0.1
            }
        };

        sendProgress(tabId, 40, "Sending request...");

        const res = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        sendProgress(tabId, 60, "Analyzing with AI...");

        if (!res.ok) {
            const errorText = await res.text();
            return { error: "Gemini API Error: " + res.status + " → " + errorText };
        }

        const data = await res.json();

        sendProgress(tabId, 75, "Processing results...");

        let output =
            data?.candidates?.[0]?.content?.parts?.[0]?.text ||
            "No analysis received.";

        // Extract truth score
        const scoreMatch = output.match(/Truth Score:\s*(\d+)\/10/i);
        const truthScore = scoreMatch ? scoreMatch[1] : "N/A";

        sendProgress(tabId, 85, "Gathering sources...");

        // Extract real citations
        const grounding =
            data?.candidates?.[0]?.groundingMetadata?.groundingChunks || [];

        let sourcesText = "";
        grounding.forEach((chunk, i) => {
            if (chunk.web && chunk.web.title && chunk.web.uri) {
                sourcesText += `${i + 1}. ${chunk.web.title} - ${chunk.web.uri}\n`;
            }
        });

        if (sourcesText.trim().length) {
            output += `\n**Sources:**\n${sourcesText}`;
        }

        return {
            result: output,
            truthScore: truthScore
        };
    } catch (err) {
        return { error: "Network/Fetch failed: " + err.message };
    }
}

// Function to download log as JSON (can be called manually or automatically)
function downloadLog() {
    if (analysisLog.length === 0) return;
    
    const logData = JSON.stringify(analysisLog, null, 2);
    const blob = new Blob([logData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    chrome.downloads.download({
        url: url,
        filename: `truetrace_log_${new Date().toISOString().split('T')[0]}.json`,
        saveAs: true
    });
}