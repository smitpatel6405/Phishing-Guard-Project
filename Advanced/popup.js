// Popup script for PhishGuard extension
// Handles the popup UI and communicates with background script

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const currentUrl = document.getElementById('currentUrl');
    const urlText = document.getElementById('urlText');
    const analysisResult = document.getElementById('analysisResult');
    const resultIcon = document.getElementById('resultIcon');
    const resultText = document.getElementById('resultText');
    const confidence = document.getElementById('confidence');
    const decision = document.getElementById('decision');
    const reasonValue = document.getElementById('reasonValue');
    const thresholdValue = document.getElementById('thresholdValue');
    const allowlistedValue = document.getElementById('allowlistedValue');
    const contentFlagsValue = document.getElementById('contentFlagsValue');
    const features = document.getElementById('features');
    const featuresList = document.getElementById('featuresList');
    const loading = document.getElementById('loading');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    const visualScanBtn = document.getElementById('visualScanBtn');
    const visualConsent = document.getElementById('visualConsent');
    const whySection = document.getElementById('whySection');
    const reasonsList = document.getElementById('reasonsList');
    
    let currentTab = null;
    let currentAnalysis = null;
    
    // Initialize popup
    function initializePopup() {
        // Check backend health
        checkBackendHealth();
        
        // Get current tab and analyze
        getCurrentTab();
        
        // Set up event listeners
        analyzeBtn.addEventListener('click', analyzeCurrentPage);
        refreshBtn.addEventListener('click', refreshAnalysis);
        visualScanBtn.addEventListener('click', runVisualScan);
        // Load saved consent
        chrome.storage.sync.get(['visualConsent'], (data) => {
            if (typeof data.visualConsent === 'boolean') {
                visualConsent.checked = data.visualConsent;
            }
        });
        visualConsent.addEventListener('change', () => {
            chrome.storage.sync.set({ visualConsent: visualConsent.checked });
        });
    // Trigger visual scan via background (capture screenshot)
    function runVisualScan() {
        if (!visualConsent.checked) {
            showError('Enable consent to allow screenshot for visual scan');
            return;
        }
        if (!currentTab || !currentTab.id) {
            showError('No active tab for visual scan');
            return;
        }
        showLoading();
        chrome.runtime.sendMessage({ action: 'run_visual_scan', tabId: currentTab.id }, function(response) {
            hideLoading();
            if (response && response.success) {
                // Display result similarly to URL analysis, but show visual flags
                const result = response.result || {};
                // Attach visual flags to content flags for unified display
                if (!result.content_flags) result.content_flags = {};
                if (result.visual_flags) {
                    Object.assign(result.content_flags, result.visual_flags);
                }
                // Map visual_score to confidence-like percentage for UI
                if (typeof result.visual_score === 'number' && result.visual_score >= 0) {
                    result.confidence = Math.round((1 - result.visual_score) * 100);
                    result.prediction = result.visual_score >= 0.85 ? 'phishing' : (result.visual_score >= 0.5 ? 'unknown' : 'legitimate');
                    result.reason = result.reason || 'visual_analysis';
                }
                displayAnalysisResult(result);
            } else {
                showError('Visual scan failed' + (response && response.error ? (': ' + response.error) : ''));
            }
        });
    }
    }
    
    // Check if backend is available
    function checkBackendHealth() {
        chrome.runtime.sendMessage({action: 'check_backend_health'}, function(response) {
            if (response && response.success) {
                if (response.healthy) {
                    statusIndicator.className = 'status-indicator status-online';
                    statusText.textContent = 'Backend Online';
                } else {
                    statusIndicator.className = 'status-indicator status-offline';
                    statusText.textContent = 'Backend Offline';
                }
            } else {
                statusIndicator.className = 'status-indicator status-offline';
                statusText.textContent = 'Backend Error';
            }
        });
    }
    
    // Get current active tab
    function getCurrentTab() {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0]) {
                currentTab = tabs[0];
                displayCurrentUrl(currentTab.url);
                
                // Auto-analyze the current page
                analyzeCurrentPage();
            }
        });
    }
    
    // Display current URL
    function displayCurrentUrl(url) {
        if (url) {
            // Truncate long URLs for display
            const displayUrl = url.length > 50 ? url.substring(0, 47) + '...' : url;
            urlText.textContent = displayUrl;
            urlText.title = url; // Full URL on hover
        } else {
            urlText.textContent = 'No URL available';
        }
    }
    
    // Analyze current page
    function analyzeCurrentPage() {
        if (!currentTab || !currentTab.url) {
            showError('No page to analyze');
            return;
        }
        
        // Skip certain URLs
        if (currentTab.url.startsWith('chrome://') || 
            currentTab.url.startsWith('chrome-extension://') ||
            currentTab.url.startsWith('about:') ||
            currentTab.url.startsWith('data:')) {
            showError('Cannot analyze this type of page');
            return;
        }
        
        // Show loading state
        showLoading();
        
        // Send message to content script to analyze
        chrome.tabs.sendMessage(currentTab.id, {action: 'analyze_current_url'}, function(response) {
            if (chrome.runtime.lastError) {
                // Content script not ready, try direct analysis
                analyzeUrlDirectly(currentTab.url);
            } else if (response && response.success) {
                // Content script handled it
                console.log('Content script analysis initiated');
            } else {
                // Fallback to direct analysis
                analyzeUrlDirectly(currentTab.url);
            }
        });
    }
    
    // Analyze URL directly through background script
    function analyzeUrlDirectly(url) {
        chrome.runtime.sendMessage({
            action: 'analyze_url',
            url: url
        }, function(response) {
            if (response && response.success) {
                displayAnalysisResult(response.result);
            } else {
                showError('Analysis failed: ' + (response?.error || 'Unknown error'));
            }
        });
    }
    
    // Refresh analysis
    function refreshAnalysis() {
        if (currentTab && currentTab.url) {
            analyzeCurrentPage();
        }
    }
    
    // Display analysis result
    function displayAnalysisResult(result) {
        // Hide loading
        hideLoading();
        
        // Store current analysis
        currentAnalysis = result;
        
        // Set result icon and text
        if (result.prediction === 'phishing') {
            resultIcon.textContent = '⚠️';
            resultText.textContent = 'PHISHING DETECTED!';
            analysisResult.className = 'analysis-result result-phishing';
        } else if (result.prediction === 'legitimate') {
            resultIcon.textContent = '✅';
            resultText.textContent = 'SAFE SITE';
            analysisResult.className = 'analysis-result result-safe';
        } else {
            resultIcon.textContent = '❓';
            resultText.textContent = 'UNKNOWN';
            analysisResult.className = 'analysis-result result-unknown';
        }
        
        // Set confidence
        if (result.confidence !== undefined) {
            confidence.textContent = `Confidence: ${result.confidence}%`;
        } else {
            confidence.textContent = 'Confidence: N/A';
        }
        
        // Show result
        analysisResult.style.display = 'block';
        
        // Display features if available
        if (result.features && Object.keys(result.features).length > 0) {
            displayFeatures(result.features);
        }

        // Decision details
        reasonValue.textContent = result.reason || '-';
        thresholdValue.textContent = (typeof result.threshold === 'number') ? `${result.threshold}%` : '-';
        allowlistedValue.textContent = result.allowlisted ? 'Yes' : 'No';
        if (result.content_flags && Object.keys(result.content_flags).length > 0) {
            const flags = Object.entries(result.content_flags)
                .map(([k, v]) => `${k}: ${v}`)
                .join('\n');
            contentFlagsValue.textContent = flags;
        } else {
            contentFlagsValue.textContent = '-';
        }
        decision.style.display = 'block';

        // Build human-readable reasons list (URL features + policy + reputation)
        buildReasonsList(result);
        whySection.style.display = 'block';
    }

    function buildReasonsList(result) {
        reasonsList.innerHTML = '';
        const items = [];

        // URL feature-based reasons
        if (result.features) {
            const f = result.features;
            if (f.has_https) items.push({t: 'Uses HTTPS (secure connection)', ok: true});
            else items.push({t: 'No HTTPS (connection not secure)', ok: false});
            if (f.has_ip_address) items.push({t: 'URL contains IP address', ok: false});
            if (f.number_of_dots >= 3) items.push({t: 'Unusually many dots in domain', ok: false});
            if (f.has_subdomain) items.push({t: 'Has subdomain (not inherently bad)', ok: true});
            if (f.has_suspicious_words) items.push({t: 'Contains suspicious words (login/secure/update etc.)', ok: false});
            if (f.path_length > 60) items.push({t: 'Very long path', ok: false});
        }

        // Policy reasons
        if (result.allowlisted) items.push({t: 'Known safe domain (allowlisted)', ok: true});
        if (result.reason === 'below_threshold') items.push({t: 'Model not confident enough to call phishing (below threshold)', ok: true});
        if (result.reason === 'model' && result.prediction === 'phishing') items.push({t: 'Model is highly confident this is phishing', ok: false});

        // Content heuristics
        if (result.content_flags) {
            if (result.content_flags.many_iframes) items.push({t: `Many iframes (${result.content_flags.many_iframes})`, ok: false});
            if (result.content_flags.many_external_scripts) items.push({t: `Many external scripts (${result.content_flags.many_external_scripts})`, ok: false});
            if (result.content_flags.suspicious_script_hosts) items.push({t: 'Suspicious ad/track script hosts', ok: false});
            if (result.content_flags.brand_mismatch) items.push({t: `Brand keyword on page not in domain (${result.content_flags.brand_mismatch})`, ok: false});
            if (result.content_flags.gsb) items.push({t: 'Flagged by Safe Browsing reputation', ok: false});
            if (result.content_flags.login_collects_password) items.push({t: 'Login form collects password on page', ok: false});
            if (result.content_flags.external_form_posts && result.content_flags.external_form_posts.length) items.push({t: `Forms post to external domains (${result.content_flags.external_form_posts.join(', ')})`, ok: false});
            if (result.content_flags.brand_logo_mismatch) items.push({t: `Brand logo/alt text not matching domain (${result.content_flags.brand_logo_mismatch})`, ok: false});
            if (result.content_flags.many_image_hosts) items.push({t: `Many third-party image hosts (${result.content_flags.many_image_hosts})`, ok: false});
            if (result.content_flags.urgent_language) items.push({t: 'Urgent/coercive language found (e.g., "verify now")', ok: false});
        }

        // Confidence summary
        if (typeof result.confidence === 'number') {
            items.push({t: `Confidence: ${result.confidence}%`, ok: result.prediction !== 'phishing'});
        }

        // Render list
        items.forEach(it => {
            const row = document.createElement('div');
            row.className = 'feature-item';
            const label = document.createElement('span');
            label.className = 'feature-label';
            label.textContent = it.ok ? '✔' : '⚠';
            const val = document.createElement('span');
            val.className = 'feature-value';
            val.textContent = it.t;
            row.appendChild(label);
            row.appendChild(val);
            reasonsList.appendChild(row);
        });
    }
    
    // Display URL features
    function displayFeatures(features) {
        featuresList.innerHTML = '';
        
        const featureLabels = {
            'url_length': 'URL Length',
            'number_of_dots': 'Number of Dots',
            'has_https': 'HTTPS',
            'has_ip_address': 'IP Address',
            'has_www': 'WWW',
            'has_subdomain': 'Subdomain',
            'domain_length': 'Domain Length',
            'path_length': 'Path Length',
            'has_suspicious_words': 'Suspicious Words'
        };
        
        for (const [key, value] of Object.entries(features)) {
            const featureItem = document.createElement('div');
            featureItem.className = 'feature-item';
            
            const label = document.createElement('span');
            label.className = 'feature-label';
            label.textContent = featureLabels[key] || key;
            
            const valueElement = document.createElement('span');
            valueElement.className = 'feature-value';
            valueElement.textContent = value;
            
            featureItem.appendChild(label);
            featureItem.appendChild(valueElement);
            featuresList.appendChild(featureItem);
        }
        
        features.style.display = 'block';
    }
    
    // Show loading state
    function showLoading() {
        loading.style.display = 'block';
        analysisResult.style.display = 'none';
        features.style.display = 'none';
    }
    
    // Hide loading state
    function hideLoading() {
        loading.style.display = 'none';
    }
    
    // Show error message
    function showError(message) {
        hideLoading();
        
        // Remove existing error
        const existingError = document.querySelector('.error');
        if (existingError) {
            existingError.remove();
        }
        
        // Create error element
        const error = document.createElement('div');
        error.className = 'error';
        error.textContent = message;
        
        // Insert after current URL
        currentUrl.parentNode.insertBefore(error, currentUrl.nextSibling);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (error.parentNode) {
                error.remove();
            }
        }, 5000);
    }
    
    // Listen for messages from content script
    chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
        if (request.action === 'analysis_complete') {
            displayAnalysisResult(request.result);
        }
    });
    
    // Initialize popup
    initializePopup();
    
    // Refresh backend health every 30 seconds
    setInterval(checkBackendHealth, 30000);
}); 