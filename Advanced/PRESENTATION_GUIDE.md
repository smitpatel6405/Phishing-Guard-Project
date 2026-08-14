# PhishGuard - Real-time Phishing Detection System
## Faculty Presentation Guide

### 🎯 **Project Overview**
**PhishGuard** is a comprehensive real-time phishing detection system that combines machine learning algorithms with browser extension technology to protect users from malicious websites.

---

## 🏗️ **System Architecture**

### **1. Backend API (Python Flask)**
- **Framework**: Flask 2.3.3
- **Language**: Python 3.8
- **Purpose**: Machine learning model server and API endpoint
- **Port**: 5000

### **2. Browser Extension (JavaScript)**
- **Platform**: Chrome Extension (Manifest V3)
- **Languages**: JavaScript (ES6+), HTML5, CSS3
- **Components**: Background Script, Content Script, Popup UI

### **3. Machine Learning Model**
- **Algorithm**: Random Forest Classifier
- **Library**: Scikit-learn 1.3.0
- **Features**: 9 URL-based features

---

## 🤖 **Machine Learning Algorithm Details**

### **Algorithm: Random Forest Classifier**

**Why Random Forest?**
- **Ensemble Method**: Combines multiple decision trees for better accuracy
- **Robust**: Handles overfitting well
- **Feature Importance**: Can identify which URL features are most suspicious
- **Binary Classification**: Perfect for phishing vs legitimate classification

**Technical Specifications:**
```python
RandomForestClassifier(
    n_estimators=10,      # 10 decision trees
    random_state=42,      # Reproducible results
    criterion='gini'      # Splitting criterion
)
```

### **Feature Engineering (9 Features)**

1. **URL Length** (`url_length`)
   - Longer URLs often indicate suspicious sites
   - Phishing sites use long URLs to hide malicious content

2. **Number of Dots** (`number_of_dots`)
   - Excessive dots suggest subdomain abuse
   - Example: `secure-paypal-verification.com`

3. **HTTPS Status** (`has_https`)
   - Legitimate sites typically use HTTPS
   - Phishing sites often use HTTP

4. **IP Address Presence** (`has_ip_address`)
   - Direct IP addresses are suspicious
   - Example: `http://192.168.1.1/login`

5. **WWW Prefix** (`has_www`)
   - Presence of www subdomain
   - Legitimate sites often use www

6. **Subdomain Detection** (`has_subdomain`)
   - Multiple subdomains can be suspicious
   - Example: `secure.paypal.verification.com`

7. **Domain Length** (`domain_length`)
   - Very long or very short domains are suspicious
   - Normal domains are typically 5-20 characters

8. **Path Length** (`path_length`)
   - Long paths can hide malicious content
   - Example: `/very/long/path/to/hide/malicious/content`

9. **Suspicious Words** (`has_suspicious_words`)
   - Keywords like 'secure', 'account', 'banking', 'login'
   - Often used in phishing attempts

---

## 🛡️ **Multi-Layer Security Approach**

### **Layer 1: Allowlist/Denylist**
```python
ALLOWLISTED_DOMAINS = {
    'google.com', 'paypal.com', 'microsoft.com', 'github.com',
    'wikipedia.org', 'amazon.com', 'apple.com', 'facebook.com'
}
```
- **Instant Protection**: Known safe domains bypass ML analysis
- **Performance**: Reduces computational load
- **Reliability**: 99% confidence for allowlisted domains

### **Layer 2: Machine Learning Analysis**
- **Confidence Threshold**: 80% (configurable)
- **Feature Extraction**: Real-time URL analysis
- **Prediction**: Binary classification (phishing/legitimate)

### **Layer 3: Content Heuristics**
```python
# Page content analysis
- iframe_count >= 10: suspicious
- external_scripts >= 8: suspicious  
- brand_mismatch: suspicious
```

### **Layer 4: Reputation API (Optional)**
- **Google Safe Browsing API**: External threat intelligence
- **Real-time Updates**: Latest threat data
- **High Confidence**: 95% confidence for API-flagged sites

---

## 💻 **Technology Stack**

### **Backend Technologies**
- **Python 3.8**: Core language
- **Flask 2.3.3**: Web framework
- **Scikit-learn 1.3.0**: Machine learning
- **Pandas 2.0.3**: Data processing
- **Flask-CORS 4.0.0**: Cross-origin requests
- **Requests 2.32.4**: HTTP client

### **Frontend Technologies**
- **JavaScript ES6+**: Extension logic
- **HTML5**: Popup interface
- **CSS3**: Styling and animations
- **Chrome Extension API**: Browser integration

### **Development Tools**
- **Docker**: Containerization
- **Gunicorn**: Production WSGI server
- **PowerShell**: Windows automation scripts

---

## 🔄 **Real-time Processing Flow**

### **1. URL Capture**
```javascript
// Content script captures URL on page load
window.location.href → background.js
```

### **2. Feature Extraction**
```python
def extract_features(url):
    # Parse URL components
    # Calculate 9 features
    # Return feature vector
```

### **3. ML Prediction**
```python
# Load pre-trained model
prediction = model.predict([feature_vector])
confidence = model.predict_proba([feature_vector])
```

### **4. Multi-layer Decision**
```python
if domain in ALLOWLIST:
    return "SAFE" (99% confidence)
elif domain in DENYLIST:
    return "PHISHING" (99% confidence)
elif ml_confidence >= 80%:
    return "PHISHING" (ml_confidence)
elif content_heuristics_suspicious:
    return "PHISHING" (85% confidence)
else:
    return "SAFE" (ml_confidence)
```

### **5. User Notification**
- **Red Banner**: High confidence phishing
- **Yellow Banner**: Caution (low confidence)
- **Green Banner**: Safe site

---

## 📊 **Performance Metrics**

### **Model Performance**
- **Training Data**: 100 samples (dummy data for demo)
- **Features**: 9 URL-based features
- **Algorithm**: Random Forest (10 trees)
- **Prediction Time**: <100ms per URL

### **System Performance**
- **API Response Time**: <200ms
- **Extension Load Time**: <1 second
- **Memory Usage**: <50MB
- **Cache Duration**: 5 minutes

---

## 🚀 **Key Features & Innovations**

### **1. Real-time Analysis**
- Automatic URL analysis on every page visit
- No user intervention required
- Instant visual feedback

### **2. Multi-layer Security**
- Allowlist/Denylist bypass
- ML-based classification
- Content heuristics
- External reputation checks

### **3. User-friendly Interface**
- Color-coded warnings (Red/Yellow/Green)
- Detailed decision explanations
- Confidence percentages
- Dismissible notifications

### **4. Configurable Parameters**
- Environment-based configuration
- Adjustable confidence thresholds
- Customizable allowlists/denylists

### **5. Cross-platform Compatibility**
- Chrome extension (Manifest V3)
- Windows/Linux/Mac support
- Docker containerization

---

## 🔧 **Installation & Setup**

### **Backend Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Start Flask server
python app.py
# Server runs on http://localhost:5000
```

### **Extension Setup**
1. Open Chrome → `chrome://extensions/`
2. Enable Developer Mode
3. Click "Load unpacked"
4. Select project folder
5. Extension ready!

---

## 📈 **Future Enhancements**

### **1. Advanced ML Models**
- Deep Learning (Neural Networks)
- Support Vector Machines
- Ensemble methods

### **2. Enhanced Features**
- Page content analysis
- Image recognition
- Behavioral analysis

### **3. Multi-browser Support**
- Firefox extension
- Safari extension
- Edge extension

### **4. Cloud Integration**
- Real-time threat intelligence
- Centralized logging
- User analytics

---

## 🎓 **Academic Significance**

### **Research Areas**
- **Cybersecurity**: Phishing detection and prevention
- **Machine Learning**: Feature engineering and classification
- **Web Security**: Browser extension development
- **User Experience**: Real-time security interfaces

### **Learning Outcomes**
- Full-stack development (Python + JavaScript)
- Machine learning implementation
- Browser extension development
- API design and integration
- Security system architecture

---

## 📝 **Presentation Tips**

### **Demo Flow**
1. **Show Backend**: API endpoints and ML model
2. **Load Extension**: Chrome extension installation
3. **Test Safe Site**: Google.com (green banner)
4. **Test Suspicious Site**: Long URL with suspicious words
5. **Show Popup**: Detailed analysis and features
6. **Explain Algorithm**: Random Forest and features

### **Key Points to Emphasize**
- **Real-time Protection**: Automatic analysis
- **Multi-layer Security**: Multiple detection methods
- **User-friendly**: Visual feedback and explanations
- **Scalable**: Configurable and extensible
- **Academic Value**: Combines ML, security, and web development

---

## 🔗 **Technical Documentation**

- **API Documentation**: Available at `http://localhost:5000/`
- **Source Code**: Well-commented and documented
- **Setup Guide**: `SETUP_GUIDE.md`
- **Test Scripts**: Automated testing included

---

*This system demonstrates practical application of machine learning in cybersecurity, combining theoretical knowledge with real-world implementation.*



