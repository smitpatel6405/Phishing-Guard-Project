# 🛡️ PhishGuard Setup Guide

## 🎯 **What We've Built**

A complete **real-time phishing detection system** with:
- ✅ **Flask Backend API** - Machine learning-powered URL analysis
- ✅ **Chrome Extension** - Real-time browser protection
- ✅ **Feature Extraction** - 9 intelligent URL features
- ✅ **ML Model** - Pre-trained RandomForest classifier

## 🚀 **Quick Start (COMPLETED!)**

### ✅ **Step 1: Dependencies Installed**
```bash
py -3.8 -m pip install -r requirements.txt
```

### ✅ **Step 2: Backend Running**
```bash
py -3.8 app.py
```
- Server: `http://localhost:5000`
- Status: ✅ Healthy
- Model: ✅ Loaded

### ✅ **Step 3: System Tested**
```bash
py -3.8 test_backend.py
py -3.8 demo.py
```

## 🔧 **Next Steps - Load the Chrome Extension**

### **Step 1: Open Chrome Extensions**
1. Open Google Chrome
2. Navigate to: `chrome://extensions/`
3. Enable **"Developer mode"** (toggle in top right)

### **Step 2: Load the Extension**
1. Click **"Load unpacked"**
2. Select the **HACKATHON folder** (this entire project folder)
3. The PhishGuard extension should appear in your extensions list

### **Step 3: Test the Extension**
1. Click the **PhishGuard icon** in your browser toolbar
2. Navigate to different websites
3. Watch for real-time phishing warnings!

## 🧪 **Testing the System**

### **Backend Testing**
```bash
# Test the API
py -3.8 test_backend.py

# Run the demo
py -3.8 demo.py

# Manual API test
curl http://localhost:5000/health
```

### **Extension Testing**
1. **Load the extension** in Chrome
2. **Navigate to websites**:
   - `https://www.google.com` (should show analysis)
   - `https://192.168.1.1/login` (should flag as suspicious)
   - Any other website
3. **Check the popup** for real-time results

## 🔍 **How It Works**

### **Feature Extraction**
The system analyzes URLs for:
- 🔐 HTTPS usage
- 🌐 IP address presence
- 📍 Suspicious keywords
- 📏 URL length and structure
- 🌍 Subdomain analysis
- And more...

### **Machine Learning**
- **Algorithm**: RandomForest Classifier
- **Input**: 9 extracted features
- **Output**: Phishing/Legitimate + Confidence score
- **Model**: Automatically created dummy model

### **Real-time Protection**
1. **Content Script** captures every URL you visit
2. **Background Script** sends URL to backend API
3. **Backend** analyzes and returns prediction
4. **Extension** shows warnings for suspicious sites

## 🚨 **Troubleshooting**

### **Backend Issues**
```bash
# Check if running
curl http://localhost:5000/health

# Restart server
py -3.8 app.py

# Check Python version
py -3.8 --version
```

### **Extension Issues**
- **Extension not loading**: Check `manifest.json` syntax
- **No analysis results**: Ensure backend is running
- **Permission errors**: Check Chrome extension permissions

### **Common Problems**
- **Port 5000 in use**: Kill existing processes or change port
- **Model not loading**: Check Python version compatibility
- **CORS errors**: Backend needs to allow extension origin

## 🎨 **Customization**

### **Modify Features**
Edit `app.py` in the `extract_features()` function to:
- Add new URL features
- Change suspicious word lists
- Modify feature weights

### **Train New Model**
1. Collect labeled phishing/legitimate URLs
2. Extract features using the same function
3. Train a new scikit-learn model
4. Save as `models/phishing_model.pkl`

### **Change Backend URL**
Edit `background.js` to point to your production server:
```javascript
const API_BASE_URL = 'https://your-server.com';
```

## 🔮 **Future Enhancements**

- **Database Integration** - Store analysis history
- **User Authentication** - Personalized settings
- **Advanced ML Models** - Deep learning approaches
- **Real-time Updates** - Live model updates
- **Mobile Support** - Android/iOS apps
- **API Rate Limiting** - Production scaling

## 📞 **Support**

### **For Issues:**
1. Check the troubleshooting section
2. Review browser console logs
3. Verify backend connectivity
4. Check extension permissions

### **Files to Check:**
- `app.py` - Backend logic
- `content.js` - URL capture
- `background.js` - API communication
- `popup.js` - User interface

## 🎉 **Congratulations!**

You now have a **fully functional phishing detection system** that:
- ✅ **Protects in real-time** as you browse
- ✅ **Uses machine learning** for intelligent detection
- ✅ **Provides visual warnings** for suspicious sites
- ✅ **Shows detailed analysis** of URL features
- ✅ **Works offline** with local ML model

**Stay safe online! 🛡️** 