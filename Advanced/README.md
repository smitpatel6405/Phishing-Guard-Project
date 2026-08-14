# PhishGuard - Real-Time Phishing Detection System

A comprehensive phishing detection system consisting of a Flask backend API and a Chrome browser extension that provides real-time protection against phishing websites.

## 🏗️ Project Structure

```
HACKATHON/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration for deployment
├── models/               # Directory for ML models
├── manifest.json         # Chrome extension manifest
├── content.js            # Content script for URL capture
├── background.js         # Background script for API communication
├── popup.html            # Extension popup interface
├── popup.js              # Popup functionality
├── icons/                # Extension icons
└── README.md             # This file
```

## 🚀 Features

### Backend (Flask API)
- **Feature Extraction**: Extracts 9 key features from URLs including:
  - URL length, number of dots, HTTPS usage
  - IP address detection, subdomain analysis
  - Suspicious word detection
- **Machine Learning**: Pre-trained RandomForest model for classification
- **Real-time Analysis**: RESTful API endpoint for instant URL analysis
- **Health Monitoring**: Built-in health check endpoints

### Browser Extension
- **Real-time Protection**: Automatically analyzes every webpage you visit
- **Visual Warnings**: Clear phishing alerts with confidence scores
- **Feature Display**: Shows extracted URL features for transparency
- **Backend Status**: Monitors API connectivity
- **Modern UI**: Beautiful, responsive popup interface

## 🛠️ Setup Instructions

### 1. Backend Setup

#### Prerequisites
- Python 3.8+
- pip package manager

#### Installation
```bash
# Clone or navigate to the project directory
cd HACKATHON

# Install Python dependencies
pip install -r requirements.txt

# Run the Flask application
python app.py
```

The backend will start on `http://localhost:5000`

#### API Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `POST /predict` - Phishing detection endpoint

#### Example API Usage
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### 2. Docker Deployment (Optional)

```bash
# Build the Docker image
docker build -t phishguard .

# Run the container
docker run -p 5000:5000 phishguard
```

### 3. Chrome Extension Setup

#### Installation
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" in the top right
3. Click "Load unpacked" and select the project directory
4. The PhishGuard extension should now appear in your extensions list

#### Usage
1. Click the PhishGuard extension icon in your browser toolbar
2. The extension will automatically analyze the current page
3. View results in the popup interface
4. Real-time warnings appear on suspicious pages

## 🔧 Configuration

### Backend Configuration
- **Port**: Default 5000 (configurable in `app.py`)
- **Model Path**: `models/phishing_model.pkl`
- **Features**: 9 extracted URL features

### Extension Configuration
- **Backend URL**: `http://localhost:5000` (configurable in `background.js`)
- **Cache Duration**: 5 minutes for API results
- **Health Check**: Every 5 minutes

## 📊 Feature Extraction

The system extracts the following features from URLs:

1. **url_length**: Total character count
2. **number_of_dots**: Count of dot characters
3. **has_https**: Boolean for HTTPS usage
4. **has_ip_address**: Boolean for IP address presence
5. **has_www**: Boolean for WWW subdomain
6. **has_subdomain**: Boolean for additional subdomains
7. **domain_length**: Length of the domain name
8. **path_length**: Length of the URL path
9. **has_suspicious_words**: Boolean for suspicious keywords

## 🤖 Machine Learning Model

- **Algorithm**: RandomForest Classifier
- **Features**: 9-dimensional feature vector
- **Output**: Binary classification (phishing/legitimate)
- **Confidence**: Probability scores for predictions

## 🔒 Security Features

- **HTTPS Enforcement**: Detects non-HTTPS connections
- **IP Address Detection**: Identifies suspicious IP-based URLs
- **Suspicious Word Filtering**: Flags URLs with suspicious keywords
- **Real-time Analysis**: Instant protection without delays

## 🧪 Testing

### Test the Backend
```bash
# Health check
curl http://localhost:5000/health

# Test prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"url": "https://google.com"}'
```

### Test the Extension
1. Install the extension
2. Navigate to different websites
3. Check the popup for analysis results
4. Verify real-time warnings on suspicious sites

## 🔎 Brand-aware recognition (Advanced server)

Place brand logo images and generate perceptual hashes so the Advanced visual scan can detect lookalikes:

1) Put logo images here (create folders if missing):

- `Advanced/brand_assets/<brand>/` → PNG/JPG/WebP logos (e.g., `google`, `paypal`, `amazon`, `myntra`, `boat`)

2) Generate logo hashes:

```bash
py -3.8 Advanced/create_logo_hashes.py
```

This updates `Advanced/logo_hashes.json` with pHash entries.

3) Extend brand profiles (text/domain/color rules):

- Edit `Advanced/brand_profiles.json` to add `domains`, `keywords`, and optional `colors` (hex strings).

4) Reload Advanced server (if needed):

```bash
py -3.8 Advanced/app.py
```

What the Advanced analyzer checks now:
- pHash logo match vs known brands; domain mismatch raises risk
- Favicon pHash match vs known brands; domain mismatch raises risk
- Brand profile mismatch (keywords on page vs registrable domain)
- Optional color palette cues (dominant page colors vs brand palette)
- OCR for coercive/auth phrases and brand words in images
- Login/password forms, off‑domain form posts, many third‑party assets

## 📥 Brand pages dataset

We store reference front-page HTML to help curate rules and test parsing:

- Run to fetch/update:

```bash
py -3.8 Advanced/fetch_brand_pages.py
```

This saves HTML to `Advanced/brand_pages/<brand>/index.html` and an index at `Advanced/brand_pages/index.json`.

Tip: Open these pages in a browser and save viewport/full-page screenshots to enrich `Advanced/brand_assets/<brand>/` for better visual hashing.

Color/threshold tuning:
- `Advanced/logo_hashes.json` has `threshold` (default 12). Lower is stricter.
- Visual fusion uses the higher risk between URL model and visual signals.

## 🚨 Troubleshooting

### Backend Issues
- **Port 5000 in use**: Change port in `app.py` or kill existing process
- **Model loading error**: Check `models/` directory exists
- **Dependencies missing**: Run `pip install -r requirements.txt`

### Extension Issues
- **Backend offline**: Ensure Flask server is running
- **No analysis results**: Check browser console for errors
- **Extension not loading**: Verify manifest.json syntax

### Common Problems
- **CORS errors**: Backend needs to allow extension origin
- **Permission denied**: Check extension permissions in Chrome
- **API timeouts**: Increase timeout in background.js

## 🔮 Future Enhancements

- **Database Integration**: Store analysis history
- **User Authentication**: Personalized protection settings
- **Advanced ML Models**: Deep learning approaches
- **Real-time Updates**: Live model updates
- **Mobile Support**: Android/iOS apps
- **API Rate Limiting**: Production-ready scaling

## 📝 License

This project is created for educational and research purposes. Use responsibly and in accordance with applicable laws and regulations.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review browser console logs
3. Verify backend connectivity
4. Check extension permissions

---

**⚠️ Disclaimer**: This tool is for educational purposes. Always use additional security measures and common sense when browsing the web. 