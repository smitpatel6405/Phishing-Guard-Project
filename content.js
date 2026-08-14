// Content script for PhishGuard extension
// Runs on every webpage to capture URLs and communicate with background script

(function() {
    'use strict';
    
    // Function to get current page URL
    function getCurrentUrl() {
        return window.location.href;
    }
    
    // Function to get page title
    function getPageTitle() {
        return document.title || 'Unknown Page';
    }
    
    // Function to get domain from URL
    function getDomain(url) {
        try {
            return new URL(url).hostname;
        } catch (e) {
            return url;
        }
    }
    
    // Function to send URL to background script for analysis
    function analyzeUrl(url) {
        // Collect lightweight on-page signals to assist backend reputation/content heuristics
        const metaDescTag = document.querySelector('meta[name="description"]');
        const ogSiteNameTag = document.querySelector('meta[property="og:site_name"]');
        const iframeCount = document.getElementsByTagName('iframe').length;
        const scripts = Array.from(document.getElementsByTagName('script'))
            .map(s => s.src || '')
            .filter(Boolean)
            .slice(0, 12);

        const page_signals = {
            title: getPageTitle(),
            metaDescription: metaDescTag ? metaDescTag.getAttribute('content') || '' : '',
            ogSiteName: ogSiteNameTag ? ogSiteNameTag.getAttribute('content') || '' : '',
            iframeCount: iframeCount,
            scriptHosts: scripts.map(src => {
                try { return new URL(src).hostname; } catch (e) { return src; }
            })
        };

        // Collect additional visual signals for upgraded heuristics
        const forms = Array.from(document.querySelectorAll('form'));
        const hasLoginKeywords = /login|sign\s*in|verify|authenticate|password|otp|secure/i;
        const urgentKeywords = /urgent|immediately|suspend|limited\s*time|verify\s*now|account\s*locked/i;
        const images = Array.from(document.querySelectorAll('img'));
        const brandKeywords = ['paypal','google','microsoft','apple','facebook','instagram','netflix','bank','amazon','github'];

        const passwordFields = Array.from(document.querySelectorAll('input[type="password"], input[name*="pass" i]'));
        const loginForms = forms.filter(f => hasLoginKeywords.test((f.textContent || '') + ' ' + (f.getAttribute('aria-label') || '')));
        const externalFormActions = forms
            .map(f => ({ action: f.getAttribute('action') || '', method: (f.getAttribute('method') || '').toUpperCase() }))
            .filter(x => x.action)
            .slice(0, 10);

        const imageAltTexts = images.map(img => (img.getAttribute('alt') || '').toLowerCase()).slice(0, 20);
        const imageSrcHosts = images.map(img => {
            try { return (new URL(img.src)).hostname; } catch (e) { return ''; }
        }).filter(Boolean).slice(0, 20);

        // Extra heuristics: inline event handlers, obfuscated scripts, data URLs
        const inlineEventHandlers = Array.from(document.querySelectorAll('[onclick],[onload],[onerror],[onmouseover],[onfocus],[onchange]')).length;
        const scriptTags = Array.from(document.getElementsByTagName('script')).slice(0, 20);
        const hasDataUrlAssets = !!document.documentElement.outerHTML.match(/\b(src|href)\s*=\s*["']data:/i);
        let obfuscatedScriptCount = 0;
        scriptTags.forEach(s => {
            const code = (s.textContent || '').slice(0, 4000);
            if (!s.src && code) {
                const suspiciousEval = /eval\s*\(|Function\s*\(/i.test(code);
                const hexOrAtob = /\\x[0-9A-Fa-f]{2}|atob\s*\(|btoa\s*\(/.test(code);
                const longBase64 = /[A-Za-z0-9+/]{80,}={0,2}/.test(code);
                if (suspiciousEval || hexOrAtob || longBase64) obfuscatedScriptCount += 1;
            }
        });

        const pageTextSample = ((document.body && document.body.innerText) ? document.body.innerText : '').slice(0, 4000);
        const foundUrgentLanguage = urgentKeywords.test(pageTextSample);
        const foundBrandLogoKeywords = brandKeywords.find(b => imageAltTexts.some(a => a.includes(b)));

        // Favicon URL
        const iconLink = document.querySelector('link[rel~="icon"]') || document.querySelector('link[rel="shortcut icon"]');
        const faviconUrl = iconLink ? (iconLink.getAttribute('href') || '') : '/favicon.ico';

        const visual_signals = {
            formCount: forms.length,
            loginFormCount: loginForms.length,
            passwordFieldCount: passwordFields.length,
            formActions: externalFormActions,
            imageHosts: imageSrcHosts,
            imageAltBrand: foundBrandLogoKeywords || '',
            urgentLanguage: !!foundUrgentLanguage,
            inlineEventHandlers: inlineEventHandlers,
            obfuscatedScriptCount: obfuscatedScriptCount,
            hasDataUrlAssets: !!hasDataUrlAssets,
            faviconUrl: faviconUrl
        };
        const message = {
            action: 'analyze_url',
            url: url,
            title: getPageTitle(),
            domain: getDomain(url),
            timestamp: Date.now(),
            page_signals,
            visual_signals
        };
        
        chrome.runtime.sendMessage(message, function(response) {
            if (response && response.success) {
                handleAnalysisResult(response.result);
                // Notify the extension popup so it can stop the spinner and show details
                try {
                    chrome.runtime.sendMessage({
                        action: 'analysis_complete',
                        result: response.result
                    });
                } catch (e) {
                    // no-op if popup not listening
                }
            } else {
                console.log('PhishGuard: Failed to analyze URL');
            }
        });
    }
    
    // Function to handle analysis results
    function handleAnalysisResult(result) {
        // Show red for confirmed phishing
        if (result.prediction === 'phishing') {
            showPhishingWarning(result);
            return;
        }

        // Show yellow caution when model originally leaned phishing but below threshold
        if (result && result.reason === 'below_threshold') {
            showCautionIndicator(result);
            return;
        }

        // New policy: if legitimate but confidence < 70% (and not allowlisted), show caution (yellow)
        const isLegit = result.prediction === 'legitimate';
        const confidencePct = typeof result.confidence === 'number' ? result.confidence : 0;
        const isAllowlisted = !!result.allowlisted;
        if (isLegit && !isAllowlisted && confidencePct < 70) {
            showCautionIndicator(result);
            return;
        }

        // Otherwise show green safe indicator (including allowlisted domains)
        showSafeIndicator(result);
    }
    
    // Function to show phishing warning
    function showPhishingWarning(result) {
        // Remove existing warning if any
        removeExistingWarning();
        
        const warning = document.createElement('div');
        warning.id = 'phishguard-warning';
        warning.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 15px;
            text-align: center;
            font-family: Arial, sans-serif;
            font-size: 16px;
            font-weight: bold;
            z-index: 999999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideDown 0.5s ease-out;
        `;
        
        warning.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                <span style="font-size: 20px;">⚠️</span>
                <span>WARNING: This site may be a phishing attempt!</span>
                <span style="font-size: 20px;">⚠️</span>
            </div>
            <div style="margin-top: 8px; font-size: 14px; opacity: 0.9;">
                Confidence: ${result.confidence}% | 
                <button id="phishguard-dismiss" style="background: rgba(255,255,255,0.2); border: 1px solid white; color: white; padding: 4px 12px; border-radius: 4px; cursor: pointer; margin-left: 10px;">Dismiss</button>
            </div>
        `;
        
        // Add CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideDown {
                from { transform: translateY(-100%); }
                to { transform: translateY(0); }
            }
        `;
        document.head.appendChild(style);
        
        document.body.appendChild(warning);
        
        // Add dismiss functionality
        document.getElementById('phishguard-dismiss').addEventListener('click', function() {
            removeExistingWarning();
        });
        
        // Auto-dismiss after 30 seconds
        setTimeout(() => {
            removeExistingWarning();
        }, 30000);
    }
    
    // Function to show safe indicator
    function showSafeIndicator(result) {
        // Remove existing warning if any
        removeExistingWarning();
        
        const indicator = document.createElement('div');
        indicator.id = 'phishguard-safe';
        indicator.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #2ecc71, #27ae60);
            color: white;
            padding: 12px;
            text-align: center;
            font-family: Arial, sans-serif;
            font-size: 14px;
            z-index: 999999;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            animation: slideDown 0.5s ease-out;
        `;
        
        indicator.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                <span style="font-size: 18px;">✅</span>
                <span>This site appears to be safe (${result.confidence}% confidence)</span>
            </div>
        `;
        
        document.body.appendChild(indicator);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            removeExistingWarning();
        }, 5000);
    }

    // Function to show caution (unknown) indicator
    function showCautionIndicator(result) {
        // Remove existing banners if any
        removeExistingWarning();

        const caution = document.createElement('div');
        caution.id = 'phishguard-caution';
        caution.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #f1c40f, #f39c12);
            color: #2c3e50;
            padding: 14px;
            text-align: center;
            font-family: Arial, sans-serif;
            font-size: 14px;
            font-weight: bold;
            z-index: 999999;
            box-shadow: 0 3px 10px rgba(0,0,0,0.25);
            animation: slideDown 0.5s ease-out;
        `;

        caution.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: center; gap: 10px;">
                <span style="font-size: 18px;">⚠️</span>
                <span>CAUTION: This site looks unusual. Proceed carefully.</span>
            </div>
            <div style="margin-top: 6px; font-size: 13px; opacity: 0.9;">
                Confidence: ${result.confidence}% (below threshold)
                <button id="phishguard-caution-dismiss" style="background: rgba(0,0,0,0.1); border: 1px solid rgba(0,0,0,0.2); color: #2c3e50; padding: 3px 10px; border-radius: 4px; cursor: pointer; margin-left: 10px;">Dismiss</button>
            </div>
        `;

        document.body.appendChild(caution);

        document.getElementById('phishguard-caution-dismiss').addEventListener('click', function() {
            removeExistingWarning();
        });

        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            removeExistingWarning();
        }, 10000);
    }
    
    // Function to remove existing warning/indicator
    function removeExistingWarning() {
        const existingWarning = document.getElementById('phishguard-warning');
        const existingSafe = document.getElementById('phishguard-safe');
        const existingCaution = document.getElementById('phishguard-caution');
        
        if (existingWarning) {
            existingWarning.remove();
        }
        if (existingSafe) {
            existingSafe.remove();
        }
        if (existingCaution) {
            existingCaution.remove();
        }
    }
    
    // Function to initialize URL analysis
    function initializeAnalysis() {
        const currentUrl = getCurrentUrl();
        
        // Skip analysis for certain URLs
        if (currentUrl.startsWith('chrome://') || 
            currentUrl.startsWith('chrome-extension://') ||
            currentUrl.startsWith('about:') ||
            currentUrl.startsWith('data:')) {
            return;
        }
        
        // Analyze the current URL
        analyzeUrl(currentUrl);
    }
    
    // Listen for page load completion
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeAnalysis);
    } else {
        initializeAnalysis();
    }
    
    // Listen for navigation events (for SPA support)
    let lastUrl = location.href;
    new MutationObserver(() => {
        const url = location.href;
        if (url !== lastUrl) {
            lastUrl = url;
            setTimeout(initializeAnalysis, 1000); // Delay to ensure page is loaded
        }
    }).observe(document, {subtree: true, childList: true});
    
    // Listen for messages from background script
    chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
        if (request.action === 'analyze_current_url') {
            const currentUrl = getCurrentUrl();
            analyzeUrl(currentUrl);
            sendResponse({success: true, url: currentUrl});
        }
        if (request.action === 'scroll_to' && typeof request.y === 'number') {
            window.scrollTo({ top: request.y, behavior: 'instant' });
            setTimeout(() => sendResponse && sendResponse({ ok: true }), 200);
            return true;
        }
        if (request.action === 'sync_result' && request.result) {
            // Apply the same decision banner the popup shows
            const r = request.result;
            // Determine current page severity (phishing > caution > safe)
            const hasPhish = !!document.getElementById('phishguard-warning');
            const hasCaution = !!document.getElementById('phishguard-caution');
            const currentSeverity = hasPhish ? 3 : (hasCaution ? 2 : 1);
            const targetSeverity = (r.prediction === 'phishing') ? 3 : (r.prediction === 'legitimate' ? 1 : 2);

            // Never downgrade risk: only update if equal or higher severity
            if (targetSeverity < currentSeverity) {
                sendResponse && sendResponse({success: true, skipped: 'kept_higher_risk'});
                return true;
            }

            if (r.prediction === 'phishing') {
                showPhishingWarning(r);
            } else if (r.prediction === 'legitimate') {
                // If legitimate but low confidence, show caution; else show safe
                const conf = typeof r.confidence === 'number' ? r.confidence : 0;
                if (!r.allowlisted && conf < 70) showCautionIndicator(r);
                else showSafeIndicator(r);
            } else {
                showCautionIndicator(r);
            }
            sendResponse({success: true});
        }
        return true;
    });
    
    console.log('PhishGuard content script loaded successfully');
})(); 