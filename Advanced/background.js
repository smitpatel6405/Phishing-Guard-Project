// Background script for PhishGuard extension
// Handles communication between content scripts and the Flask backend API

// Configuration
// Use 5000 for URL predict, 5001 for visual/fusion
const API_BASE_URL_PREDICT = 'http://localhost:5000';
const API_BASE_URL_VISUAL = 'http://localhost:5001';
const API_PREDICT_ENDPOINT = '/predict';
const API_FUSED_ENDPOINT = '/predict_fused';

// Cache for recent results to avoid repeated API calls
const resultCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// Function to check if result is cached and still valid
function getCachedResult(url) {
    const cached = resultCache.get(url);
    if (cached && (Date.now() - cached.timestamp) < CACHE_DURATION) {
        return cached.result;
    }
    return null;
}

// Function to cache a result
function cacheResult(url, result) {
    resultCache.set(url, {
        result: result,
        timestamp: Date.now()
    });
    
    // Clean up old cache entries
    const now = Date.now();
    for (const [key, value] of resultCache.entries()) {
        if (now - value.timestamp > CACHE_DURATION) {
            resultCache.delete(key);
        }
    }
}

// Function to send URL to Flask backend for analysis
async function analyzeUrlWithBackend(url, pageSignals, visualSignals) {
    try {
        const response = await fetch(`${API_BASE_URL_PREDICT}${API_PREDICT_ENDPOINT}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url, page_signals: pageSignals || null, visual_signals: visualSignals || null })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error('PhishGuard: Error calling backend API:', error);
        throw error;
    }
}

// Function to handle URL analysis
async function handleUrlAnalysis(url) {
    try {
        // Check cache first
        const cachedResult = getCachedResult(url);
        if (cachedResult) {
            console.log('PhishGuard: Using cached result for:', url);
            return cachedResult;
        }
        
        console.log('PhishGuard: Analyzing URL:', url);
        
        // Call backend API (include any page_signals sent by the content script)
        const pageSignals = (typeof lastContentRequest === 'object') ? lastContentRequest.page_signals : null;
        const visualSignals = (typeof lastContentRequest === 'object') ? lastContentRequest.visual_signals : null;
        const result = await analyzeUrlWithBackend(url, pageSignals, visualSignals);
        
        // Cache the result
        cacheResult(url, result);
        
        console.log('PhishGuard: Analysis result:', result);
        return result;
        
    } catch (error) {
        console.error('PhishGuard: Failed to analyze URL:', error);
        
        // Return a fallback result
        return {
            url: url,
            prediction: 'unknown',
            confidence: 0,
            error: error.message,
            features: {}
        };
    }
}

// Function to check if backend is available
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const health = await response.json();
            return health.status === 'healthy';
        }
        return false;
    } catch (error) {
        console.error('PhishGuard: Backend health check failed:', error);
        return false;
    }
}

// Listen for messages from content scripts
let lastContentRequest = null;
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'analyze_url') {
        const url = request.url;
        lastContentRequest = request; // store signals from content script
        
        // Validate URL
        if (!url || typeof url !== 'string') {
            sendResponse({
                success: false,
                error: 'Invalid URL provided'
            });
            return true;
        }
        
        // Handle the analysis asynchronously
        handleUrlAnalysis(url)
            .then(result => {
                sendResponse({
                    success: true,
                    result: result
                });
            })
            .catch(error => {
                sendResponse({
                    success: false,
                    error: error.message
                });
            });
        
        return true; // Keep message channel open for async response
    }
    
    if (request.action === 'check_backend_health') {
        checkBackendHealth()
            .then(isHealthy => {
                sendResponse({
                    success: true,
                    healthy: isHealthy
                });
            })
            .catch(error => {
                sendResponse({
                    success: false,
                    error: error.message
                });
            });
        
        return true;
    }
    
    if (request.action === 'get_extension_info') {
        sendResponse({
            success: true,
            info: {
                name: 'PhishGuard',
                version: '1.0.0',
                description: 'Real-time phishing detection browser extension'
            }
        });
        return true;
    }
});

// Listen for extension installation
chrome.runtime.onInstalled.addListener(function(details) {
    if (details.reason === 'install') {
        console.log('PhishGuard extension installed successfully');
        
        // Check backend health on installation
        checkBackendHealth().then(isHealthy => {
            if (!isHealthy) {
                console.warn('PhishGuard: Backend API is not available. Please ensure the Flask server is running on localhost:5000');
            } else {
                console.log('PhishGuard: Backend API is healthy');
            }
        });
    }
});

// Listen for tab updates to trigger analysis
chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
    if (changeInfo.status === 'complete' && tab.url) {
        // Skip certain URLs
        if (tab.url.startsWith('chrome://') || 
            tab.url.startsWith('chrome-extension://') ||
            tab.url.startsWith('about:') ||
            tab.url.startsWith('data:')) {
            return;
        }
        
        // Send message to content script to analyze the URL
        chrome.tabs.sendMessage(tabId, {
            action: 'analyze_current_url'
        }).catch(error => {
            // Content script might not be ready yet, ignore errors
            console.log('PhishGuard: Content script not ready yet for tab:', tabId);
        });
    }
});

// Periodic backend health check
setInterval(async () => {
    const isHealthy = await checkBackendHealth();
    if (!isHealthy) {
        console.warn('PhishGuard: Backend API health check failed');
    }
}, 5 * 60 * 1000); // Check every 5 minutes

console.log('PhishGuard background script loaded successfully'); 

// Visual scan: capture screenshot of current tab and send to backend
async function runVisualScan(tabId) {
    try {
        const imageDataUrl = await chrome.tabs.captureVisibleTab(undefined, { format: 'png', quality: 90 });
        // Gather basic DOM hints if available from last content request
        const domHints = (typeof lastContentRequest === 'object' && lastContentRequest.page_signals) ? {
            title: lastContentRequest.page_signals.title || '',
            metaDescription: lastContentRequest.page_signals.metaDescription || ''
        } : {};
        const url = (typeof lastContentRequest === 'object' && lastContentRequest.url) ? lastContentRequest.url : '';

        // Call fused endpoint to combine URL+visual in one step
        const resp = await fetch(`${API_BASE_URL_VISUAL}${API_FUSED_ENDPOINT}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, image_base64: imageDataUrl, dom_hints: domHints })
        });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const result = await resp.json();
        return { success: true, result };
    } catch (err) {
        return { success: false, error: String(err) };
    }
}

// Listen for visual scan requests from popup
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.action === 'run_visual_scan') {
        runVisualScan(request.tabId).then(sendResponse);
        return true;
    }
});