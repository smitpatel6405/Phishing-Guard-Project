# PhishGuard - Technical Summary for Faculty

## 🤖 **Machine Learning Algorithm**

### **Algorithm: Random Forest Classifier**
- **Type**: Ensemble Learning (Supervised)
- **Library**: Scikit-learn 1.3.0
- **Parameters**: 10 estimators, Gini criterion
- **Purpose**: Binary classification (Phishing vs Legitimate)

### **Why Random Forest?**
1. **Robust**: Handles overfitting better than single decision trees
2. **Feature Importance**: Can identify which URL features are most suspicious
3. **Ensemble Method**: Combines multiple trees for better accuracy
4. **Interpretable**: Easy to understand and explain decisions

---

## 🔧 **Technology Stack**

### **Backend (Python)**
- **Language**: Python 3.8
- **Framework**: Flask 2.3.3
- **ML Library**: Scikit-learn 1.3.0
- **Data Processing**: Pandas 2.0.3
- **CORS**: Flask-CORS 4.0.0
- **HTTP Client**: Requests 2.32.4

### **Frontend (JavaScript)**
- **Language**: JavaScript ES6+
- **Platform**: Chrome Extension (Manifest V3)
- **UI**: HTML5 + CSS3
- **APIs**: Chrome Extension API

### **Development Tools**
- **Containerization**: Docker
- **Production Server**: Gunicorn
- **Automation**: PowerShell scripts

---

## 📊 **Feature Engineering (9 Features)**

| Feature | Description | Why Important |
|---------|-------------|---------------|
| `url_length` | Total URL character count | Phishing sites use long URLs to hide malicious content |
| `number_of_dots` | Count of dots in URL | Excessive dots suggest subdomain abuse |
| `has_https` | HTTPS protocol presence | Legitimate sites typically use HTTPS |
| `has_ip_address` | Direct IP address in URL | Direct IPs are suspicious |
| `has_www` | WWW subdomain presence | Common in legitimate sites |
| `has_subdomain` | Multiple subdomains detected | Can indicate subdomain abuse |
| `domain_length` | Domain name character count | Very long/short domains are suspicious |
| `path_length` | URL path character count | Long paths can hide malicious content |
| `has_suspicious_words` | Keywords like 'secure', 'login' | Often used in phishing attempts |

---

## 🛡️ **Multi-Layer Security Architecture**

### **Layer 1: Allowlist/Denylist**
```python
ALLOWLISTED_DOMAINS = {'google.com', 'paypal.com', 'microsoft.com', ...}
DENYLISTED_DOMAINS = {'example-phish.com', ...}
```
- **Confidence**: 99%
- **Performance**: Instant
- **Purpose**: Bypass ML for known domains

### **Layer 2: Machine Learning**
```python
if ml_confidence >= 80%:
    return "PHISHING"
else:
    return "LEGITIMATE"
```
- **Confidence**: 80% threshold (configurable)
- **Performance**: <100ms
- **Purpose**: Core classification

### **Layer 3: Content Heuristics**
```python
# Page content analysis
if iframe_count >= 10: suspicious += 1
if external_scripts >= 8: suspicious += 1
if brand_mismatch: suspicious += 1
```
- **Confidence**: 85%
- **Performance**: Real-time
- **Purpose**: Additional validation

### **Layer 4: Reputation API**
```python
# Google Safe Browsing API
if gsb_malicious:
    return "PHISHING" (95% confidence)
```
- **Confidence**: 95%
- **Performance**: 4s timeout
- **Purpose**: External threat intelligence

---

## 🔄 **Real-time Processing Flow**

```
1. URL Capture (Content Script)
   ↓
2. Feature Extraction (9 features)
   ↓
3. Allowlist Check (Instant)
   ↓
4. ML Prediction (Random Forest)
   ↓
5. Content Heuristics (Page analysis)
   ↓
6. Reputation API (Optional)
   ↓
7. User Notification (Visual feedback)
```

---

## 📈 **Performance Metrics**

### **Model Performance**
- **Training Data**: 100 samples (demo)
- **Features**: 9 URL-based features
- **Algorithm**: Random Forest (10 trees)
- **Prediction Time**: <100ms

### **System Performance**
- **API Response**: <200ms
- **Extension Load**: <1 second
- **Memory Usage**: <50MB
- **Cache Duration**: 5 minutes

---

## 🎯 **Key Innovations**

### **1. Real-time Analysis**
- Automatic URL analysis on every page visit
- No user intervention required
- Instant visual feedback

### **2. Multi-layer Security**
- Not just ML - multiple detection methods
- Reduces false positives
- Increases detection accuracy

### **3. User Experience**
- Color-coded warnings (Red/Yellow/Green)
- Detailed explanations
- Confidence percentages
- Dismissible notifications

### **4. Configurable System**
- Environment-based configuration
- Adjustable confidence thresholds
- Customizable allowlists/denylists

---

## 🔬 **Academic Significance**

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

### **Technical Skills Demonstrated**
- **Backend Development**: Flask API, ML model integration
- **Frontend Development**: Chrome extension, JavaScript
- **Machine Learning**: Feature engineering, model training
- **Security**: Multi-layer protection, threat detection
- **DevOps**: Docker, automation scripts

---

## 🚀 **Future Enhancements**

### **Advanced ML Models**
- Deep Learning (Neural Networks)
- Support Vector Machines
- Ensemble methods

### **Enhanced Features**
- Page content analysis
- Image recognition
- Behavioral analysis

### **Multi-browser Support**
- Firefox extension
- Safari extension
- Edge extension

### **Cloud Integration**
- Real-time threat intelligence
- Centralized logging
- User analytics

---

## 📝 **Code Structure**

```
PhishGuard/
├── app.py                 # Flask backend with ML model
├── manifest.json          # Chrome extension manifest
├── background.js          # Extension background script
├── content.js            # Content script for URL capture
├── popup.html            # Extension popup UI
├── popup.js              # Popup functionality
├── requirements.txt      # Python dependencies
├── models/
│   └── phishing_model.pkl # Trained ML model
└── icons/                # Extension icons
```

---

*This system demonstrates practical application of machine learning in cybersecurity, combining theoretical knowledge with real-world implementation.*



