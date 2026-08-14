# Chrome Extension Setup Guide

## Quick Setup Steps

### 1. Backend is Already Running ✅
Your Flask backend is running successfully on http://localhost:5000

### 2. Load the Chrome Extension

1. **Open Chrome** and go to `chrome://extensions/`
2. **Enable Developer Mode** (toggle in top-right corner)
3. **Click "Load unpacked"**
4. **Select the folder**: `E:\SMIT\HACKATHON` (the folder containing manifest.json)
5. **Click "Select Folder"**

### 3. Test the Extension

1. **Click the PhishGuard icon** in Chrome toolbar
2. **Visit a test website** like:
   - https://www.google.com (should show SAFE)
   - https://www.paypal.com (should show SAFE - allowlisted)
   - Any suspicious-looking site

### 4. Troubleshooting

If you see errors in the extension:

1. **Check the Console**:
   - Right-click the extension icon → "Inspect popup"
   - Look for any red error messages

2. **Check Background Script**:
   - Go to `chrome://extensions/`
   - Find PhishGuard → Click "Inspect views: background page"
   - Look for errors in the console

3. **Common Issues**:
   - Make sure backend is running (it is!)
   - Make sure you selected the correct folder (E:\SMIT\HACKATHON)
   - Try refreshing the extension

### 5. Expected Behavior

- **Green banner**: Safe sites (high confidence legitimate)
- **Yellow banner**: Caution (low confidence or suspicious features)
- **Red banner**: Phishing detected (high confidence phishing)

The extension should automatically analyze every page you visit!



