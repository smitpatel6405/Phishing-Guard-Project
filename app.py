from flask import Flask, request, jsonify
from flask_cors import CORS
from urllib.parse import urlparse
import re
import pickle
import os
from pathlib import Path
import os
import json
import requests
import base64
from io import BytesIO

try:
    from PIL import Image
    import imagehash
except Exception:
    Image = None
    imagehash = None

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Backend safety controls ---
# Simple allowlist of well-known legitimate registrable domains
# Environment-driven config (comma-separated lists)
ENV_ALLOWLIST = os.getenv('PG_ALLOWLIST', '').strip()
ENV_DENYLIST = os.getenv('PG_DENYLIST', '').strip()

ALLOWLISTED_DOMAINS = {
    'google.com', 'paypal.com', 'microsoft.com', 'github.com', 'wikipedia.org',
    'amazon.com', 'apple.com', 'facebook.com', 'linkedin.com', 'twitter.com',
    'youtube.com', 'netflix.com', 'stackoverflow.com', 'reddit.com',
    'cloudflare.com', 'openai.com', 'gamma.app', 'amazon.com', 'amazon.in', 'netflix.com', 'primevideo.com', 'boat-lifestyle.com'
} | {d.strip().lower() for d in (ENV_ALLOWLIST.split(',') if ENV_ALLOWLIST else []) if d.strip()}

# Only return phishing when model confidence >= 80%
PHISHING_CONFIDENCE_THRESHOLD = float(os.getenv('PG_PHISHING_THRESHOLD', '0.80'))

# Optional domain denylist (forces phishing)
ENV_DENY_SET = {d.strip().lower() for d in (ENV_DENYLIST.split(',') if ENV_DENYLIST else []) if d.strip()}
DENYLISTED_DOMAINS = {
    # Examples; add domains you consider untrusted
    'example-phish.com',
} | ENV_DENY_SET

# Heuristic helpers for content/reputation signals
SUSPICIOUS_SCRIPT_HOST_KEYWORDS = ['ad', 'track', 'malware', 'click', 'counter', 'pixel']
BRAND_KEYWORDS = [
    'paypal', 'google', 'microsoft', 'apple', 'facebook', 'instagram',
    'netflix', 'bank', 'amazon', 'github'
]

# Optional Google Safe Browsing reputation check
GSB_API_KEY = os.getenv('GOOGLE_SAFE_BROWSING_API_KEY') or os.getenv('GSB_API_KEY')
GSB_ENDPOINT = 'https://safebrowsing.googleapis.com/v4/threatMatches:find'

def check_safe_browsing(url: str) -> dict:
    """Query Google Safe Browsing v4 if API key provided. Returns {'malicious': bool, 'matches': list}.
    """
    if not GSB_API_KEY:
        return {'malicious': False, 'matches': []}
    try:
        payload = {
            "client": {"clientId": "phishguard", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": [
                    "MALWARE", "SOCIAL_ENGINEERING", "POTENTIALLY_HARMFUL_APPLICATION",
                    "UNWANTED_SOFTWARE"
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }
        resp = requests.post(f"{GSB_ENDPOINT}?key={GSB_API_KEY}",
                             headers={"Content-Type": "application/json"},
                             data=json.dumps(payload), timeout=4)
        if resp.status_code != 200:
            return {'malicious': False, 'matches': []}
        data = resp.json() or {}
        matches = data.get('matches') or []
        return {'malicious': len(matches) > 0, 'matches': matches}
    except Exception:
        return {'malicious': False, 'matches': []}


def get_registrable_domain(hostname: str) -> str:
    """Best-effort extraction of the registrable domain (e.g., sub.mail.google.com -> google.com).

    Note: This is a simplified approach for demo purposes and does not use the Public Suffix List.
    """
    if not hostname:
        return ''
    host = hostname.lower().split(':')[0]
    parts = host.split('.')
    if len(parts) >= 2:
        return '.'.join(parts[-2:])
    return host

def extract_features(url):
    """
    Extract features from a URL for phishing detection.
    
    Args:
        url (str): The URL to analyze
        
    Returns:
        dict: Dictionary containing extracted features
    """
    try:
        parsed = urlparse(url)
        
        # Basic URL features
        url_length = len(url)
        number_of_dots = url.count('.')
        has_https = 1 if parsed.scheme == 'https' else 0
        
        # Check if URL contains IP address
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        has_ip_address = 1 if re.search(ip_pattern, url) else 0
        
        # Additional features
        has_www = 1 if 'www.' in url.lower() else 0
        has_subdomain = 1 if len(parsed.netloc.split('.')) > 2 else 0
        domain_length = len(parsed.netloc) if parsed.netloc else 0
        path_length = len(parsed.path) if parsed.path else 0
        
        # Check for suspicious patterns
        has_suspicious_words = 0
        suspicious_words = ['secure', 'account', 'banking', 'login', 'signin', 'update']
        for word in suspicious_words:
            if word in url.lower():
                has_suspicious_words = 1
                break
        
        features = {
            'url_length': url_length,
            'number_of_dots': number_of_dots,
            'has_https': has_https,
            'has_ip_address': has_ip_address,
            'has_www': has_www,
            'has_subdomain': has_subdomain,
            'domain_length': domain_length,
            'path_length': path_length,
            'has_suspicious_words': has_suspicious_words
        }
        
        return features
        
    except Exception as e:
        # Return default features if parsing fails
        return {
            'url_length': len(url),
            'number_of_dots': url.count('.'),
            'has_https': 0,
            'has_ip_address': 0,
            'has_www': 0,
            'has_subdomain': 0,
            'domain_length': 0,
            'path_length': 0,
            'has_suspicious_words': 0
        }

# Load the pre-trained model
def load_model():
    """Load the pre-trained phishing detection model."""
    model_path = Path(__file__).parent / 'models' / 'phishing_model.pkl'
    
    if not model_path.exists():
        # Create a dummy model for demonstration
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np
        
        # Create dummy training data
        X_dummy = np.random.rand(100, 9)  # 9 features
        y_dummy = np.random.randint(0, 2, 100)  # Binary labels
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_dummy, y_dummy)
        
        # Save the dummy model
        models_dir = Path(__file__).parent / 'models'
        models_dir.mkdir(exist_ok=True)
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        print(f"Created dummy model at {model_path}")
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    return model

# Load model at startup
try:
    model = load_model()
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/predict', methods=['POST'])
def predict():
    """
    Predict if a URL is a phishing site.
    
    Expected JSON payload:
    {
        "url": "https://example.com"
    }
    
    Returns:
        JSON response with prediction and confidence
    """
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'URL field is required'}), 400
        
        url = data['url']
        
        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400
        
        # Allowlist/Denylist short-circuits
        parsed_for_allow = urlparse(url)
        registrable = get_registrable_domain(parsed_for_allow.netloc)
        if registrable in DENYLISTED_DOMAINS:
            return jsonify({
                'url': url,
                'prediction': 'phishing',
                'confidence': 99.0,
                'features': extract_features(url),
                'allowlisted': False,
                'reason': 'domain_denylisted'
            })
        if registrable in ALLOWLISTED_DOMAINS:
            return jsonify({
                'url': url,
                'prediction': 'legitimate',
                'confidence': 99.0,
                'features': extract_features(url),
                'allowlisted': True,
                'reason': 'domain_allowlisted'
            })

        # Extract features
        features = extract_features(url)
        
        if model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Convert features to feature vector
        feature_vector = [
            features['url_length'],
            features['number_of_dots'],
            features['has_https'],
            features['has_ip_address'],
            features['has_www'],
            features['has_subdomain'],
            features['domain_length'],
            features['path_length'],
            features['has_suspicious_words']
        ]
        
        # Make prediction
        prediction = model.predict([feature_vector])[0]
        prediction_proba = model.predict_proba([feature_vector])[0]

        proba_legitimate = float(prediction_proba[0])
        proba_phishing = float(prediction_proba[1])

        # Apply threshold policy
        is_phishing_high_conf = (proba_phishing >= PHISHING_CONFIDENCE_THRESHOLD)
        if prediction == 1 and not is_phishing_high_conf:
            final_prediction = 'legitimate'
            final_confidence = proba_legitimate
            reason = 'below_threshold'
        else:
            final_prediction = 'phishing' if prediction == 1 else 'legitimate'
            final_confidence = proba_phishing if final_prediction == 'phishing' else proba_legitimate
            reason = 'model'

        # Incorporate optional page content/reputation signals
        page_signals = data.get('page_signals') if isinstance(data, dict) else None
        visual_signals = data.get('visual_signals') if isinstance(data, dict) else None
        content_flags = {}
        if page_signals:
            try:
                iframe_count = int(page_signals.get('iframeCount') or 0)
            except Exception:
                iframe_count = 0
            script_hosts = page_signals.get('scriptHosts') or []
            title_text = (page_signals.get('title') or '').lower()
            meta_desc = (page_signals.get('metaDescription') or '').lower()
            og_site = (page_signals.get('ogSiteName') or '').lower()

            suspicious_score = 0

            if iframe_count >= 10:
                suspicious_score += 1
                content_flags['many_iframes'] = iframe_count

            if isinstance(script_hosts, list) and len(script_hosts) >= 8:
                suspicious_score += 1
                content_flags['many_external_scripts'] = len(script_hosts)

            if any(any(k in (h or '').lower() for k in SUSPICIOUS_SCRIPT_HOST_KEYWORDS) for h in script_hosts):
                suspicious_score += 1
                content_flags['suspicious_script_hosts'] = True

            # Brand abuse heuristic: brand keyword in page text but not in registrable domain
            page_text = f"{title_text} {meta_desc} {og_site}"
            for brand in BRAND_KEYWORDS:
                if brand in page_text and brand not in registrable:
                    suspicious_score += 1
                    content_flags['brand_mismatch'] = brand
                    break

            if suspicious_score >= 2 and final_prediction != 'phishing':
                final_prediction = 'phishing'
                final_confidence = max(final_confidence, 0.85)
                reason = 'content_heuristics'

        # Additional upgraded visual heuristics
        if visual_signals:
            try:
                form_count = int(visual_signals.get('formCount') or 0)
            except Exception:
                form_count = 0
            try:
                login_form_count = int(visual_signals.get('loginFormCount') or 0)
            except Exception:
                login_form_count = 0
            try:
                password_field_count = int(visual_signals.get('passwordFieldCount') or 0)
            except Exception:
                password_field_count = 0

            form_actions = visual_signals.get('formActions') or []
            image_hosts = visual_signals.get('imageHosts') or []
            image_alt_brand = (visual_signals.get('imageAltBrand') or '').lower()
            urgent_language = bool(visual_signals.get('urgentLanguage'))

            visual_suspicious_score = 0

            if login_form_count >= 1 and password_field_count >= 1:
                visual_suspicious_score += 1
                content_flags['login_collects_password'] = True

            # External form posts to different host than registrable domain
            try:
                parsed = urlparse(url)
                current_host = get_registrable_domain(parsed.netloc)
            except Exception:
                current_host = ''
            external_posts = []
            if isinstance(form_actions, list):
                for action in form_actions[:10]:
                    try:
                        action_host = get_registrable_domain(urlparse(action).netloc)
                    except Exception:
                        action_host = ''
                    if action_host and current_host and action_host != current_host:
                        external_posts.append(action_host)
                if external_posts:
                    visual_suspicious_score += 1
                    content_flags['external_form_posts'] = list(sorted(set(external_posts)))

            # Mismatched brand logo in images compared to domain
            if image_alt_brand and image_alt_brand not in registrable:
                visual_suspicious_score += 1
                content_flags['brand_logo_mismatch'] = image_alt_brand

            # Many third-party image hosts
            if isinstance(image_hosts, list) and len(image_hosts) >= 15:
                visual_suspicious_score += 1
                content_flags['many_image_hosts'] = len(image_hosts)

            # Urgent coercive language present
            if urgent_language:
                visual_suspicious_score += 1
                content_flags['urgent_language'] = True

            if visual_suspicious_score >= 2 and final_prediction != 'phishing':
                final_prediction = 'phishing'
                final_confidence = max(final_confidence, 0.88)
                reason = 'visual_heuristics'

        # Reputation API (Safe Browsing) - final say if malicious
        gsb = check_safe_browsing(url)
        if gsb.get('malicious'):
            final_prediction = 'phishing'
            final_confidence = max(final_confidence, 0.95)
            reason = 'reputation_api_gsb'
            content_flags['gsb'] = True

        result = {
            'url': url,
            'prediction': final_prediction,
            'confidence': round(final_confidence * 100, 2),
            'features': features,
            'allowlisted': False,
            'reason': reason,
            'threshold': int(PHISHING_CONFIDENCE_THRESHOLD * 100),
            'content_flags': content_flags
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Prediction failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model_loaded': model is not None})

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information."""
    return jsonify({
        'message': 'Phishing Detection API',
        'endpoints': {
            'POST /predict': 'Predict if a URL is phishing',
            'POST /analyze_screen': 'Analyze a screenshot for brand/visual risks',
            'GET /health': 'Health check',
            'GET /': 'API information'
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 

# --- Advanced visual analysis (stub) ---
@app.route('/analyze_screen', methods=['POST'])
def analyze_screen():
    """Accepts a screenshot (base64 data URL or raw base64) and returns visual analysis flags.

    Expected JSON payload:
    {
        "url": "https://example.com",
        "image_base64": "data:image/png;base64,iVBORw0..." | "iVBORw0...",
        "dom_hints": {
            "title": "...",
            "metaDescription": "..."
        }
    }
    """
    try:
        payload = request.get_json() or {}
        url = payload.get('url') or ''
        image_b64 = payload.get('image_base64') or ''
        dom_hints = payload.get('dom_hints') or {}

        # Basic validation
        if not url or not image_b64:
            return jsonify({
                'error': 'url and image_base64 are required'
            }), 400

        # Normalize data URL -> pure base64 if needed
        if image_b64.startswith('data:'):
            try:
                image_b64 = image_b64.split(',', 1)[1]
            except Exception:
                pass

        # We keep this minimal: size check, optional pHash against tiny logo set, brand text vs domain
        parsed = urlparse(url)
        registrable = get_registrable_domain(parsed.netloc)

        visual_flags = {}
        reason_notes = []

        # Approximate size check
        try:
            approx_kb = len(image_b64) * 0.75 / 1024.0
            visual_flags['image_kb'] = round(approx_kb, 1)
        except Exception:
            pass

        title_text = (dom_hints.get('title') or '').lower()
        meta_desc = (dom_hints.get('metaDescription') or '').lower()
        page_text = f"{title_text} {meta_desc}"
        for brand in BRAND_KEYWORDS:
            if brand in page_text and brand not in registrable:
                visual_flags['brand_text_mismatch'] = brand
                reason_notes.append(f"Brand text '{brand}' not in domain {registrable}")
                break

        # Optional pHash match to small embedded brand set (if Pillow available)
        phash_mismatch = False
        if Image and imagehash:
            try:
                img_bytes = base64.b64decode(image_b64, validate=False)
                img = Image.open(BytesIO(img_bytes)).convert('RGB')
                # Downscale to speed
                img = img.resize((512, int(512 * img.height / max(1, img.width))), Image.BILINEAR)
                page_hash = imagehash.phash(img)
                # Placeholder for future template hashes (empty now)
                known_hashes = {}
                # If we had known brand hashes, compute min distance
                if known_hashes:
                    distances = {brand: page_hash - h for brand, h in known_hashes.items()}
                    best_brand, best_dist = min(distances.items(), key=lambda kv: kv[1])
                    visual_flags['phash_best_brand'] = best_brand
                    visual_flags['phash_distance'] = int(best_dist)
                    if best_brand not in registrable and best_dist <= 12:
                        phash_mismatch = True
            except Exception:
                pass

        # Score: raise if text mismatch or phash mismatch
        visual_score = 0.2
        if 'brand_text_mismatch' in visual_flags:
            visual_score = max(visual_score, 0.7)
        if phash_mismatch:
            visual_score = max(visual_score, 0.9)

        return jsonify({
            'url': url,
            'visual_score': round(visual_score, 2),
            'visual_flags': visual_flags,
            'reason': 'visual_text_stub' if visual_score >= 0.5 else 'visual_baseline',
        })

    except Exception as e:
        return jsonify({'error': f'Visual analysis failed: {str(e)}'}), 500