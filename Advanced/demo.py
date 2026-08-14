#!/usr/bin/env python3
"""
PhishGuard Demo Script
Showcases the phishing detection system with real examples
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"

def test_url(url, description):
    """Test a URL and display results"""
    print(f"\n🔍 Testing: {description}")
    print(f"   URL: {url}")
    
    try:
        payload = {"url": url}
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Result: {data['prediction'].upper()}")
            print(f"   📊 Confidence: {data['confidence']}%")
            
            # Show key features
            features = data['features']
            print(f"   🔐 HTTPS: {'Yes' if features['has_https'] else 'No'}")
            print(f"   🌐 IP Address: {'Yes' if features['has_ip_address'] else 'No'}")
            print(f"   📍 Suspicious Words: {'Yes' if features['has_suspicious_words'] else 'No'}")
            print(f"   📏 URL Length: {features['url_length']}")
            
        else:
            print(f"   ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Failed: {e}")

def main():
    """Run the demo"""
    print("🛡️ PhishGuard - Phishing Detection Demo")
    print("=" * 50)
    
    # Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['model_loaded']:
                print("✅ Backend is running and model is loaded!")
            else:
                print("⚠️ Backend is running but model is not loaded")
                return
        else:
            print("❌ Backend is not responding properly")
            return
    except:
        print("❌ Backend is not running. Please start it with: py -3.8 app.py")
        return
    
    print("\n🚀 Starting phishing detection tests...")
    
    # Test various types of URLs
    test_cases = [
        ("https://www.google.com", "Legitimate website (Google)"),
        ("https://www.microsoft.com", "Legitimate website (Microsoft)"),
        ("http://suspicious-site.com", "Suspicious site (no HTTPS)"),
        ("https://192.168.1.1/login", "IP-based URL (suspicious)"),
        ("https://www.bank-account-secure.com/update", "Suspicious banking URL"),
        ("https://legitimate-site.org", "Legitimate organization"),
        ("https://www.paypal-secure.com/login", "Suspicious PayPal clone"),
        ("http://free-gift-claim.com", "Suspicious free gift site"),
        ("https://www.github.com", "Legitimate developer platform"),
        ("https://10.0.0.1/admin", "Local IP admin page (suspicious)")
    ]
    
    for url, description in test_cases:
        test_url(url, description)
        time.sleep(0.5)  # Small delay between requests
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed!")
    print("\n💡 Next steps:")
    print("   1. Load the Chrome extension in your browser")
    print("   2. Navigate to different websites")
    print("   3. See real-time phishing detection in action!")
    print("\n🔧 To load the extension:")
    print("   1. Open Chrome and go to chrome://extensions/")
    print("   2. Enable 'Developer mode'")
    print("   3. Click 'Load unpacked' and select this folder")

if __name__ == "__main__":
    main() 