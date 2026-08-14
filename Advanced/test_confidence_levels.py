#!/usr/bin/env python3
"""
Test different confidence levels and show color coding
"""

import requests
import json

def test_url(url, description):
    """Test a URL and show confidence level"""
    try:
        payload = {"url": url}
        response = requests.post(
            "http://localhost:5000/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            confidence = data['confidence']
            prediction = data['prediction']
            
            # Determine color and risk level
            if prediction == 'phishing':
                if confidence >= 90:
                    color = "🔴 DARK RED"
                    risk = "EXTREMELY HIGH RISK"
                elif confidence >= 80:
                    color = "🔴 MEDIUM RED"
                    risk = "HIGH RISK"
                elif confidence >= 70:
                    color = "🔴 LIGHT RED"
                    risk = "MEDIUM-HIGH RISK"
                else:
                    color = "🔴 LIGHT RED"
                    risk = "MEDIUM RISK"
            else:
                if confidence >= 90:
                    color = "🟢 DARK GREEN"
                    risk = "VERY SAFE"
                elif confidence >= 80:
                    color = "🟢 MEDIUM GREEN"
                    risk = "SAFE"
                elif confidence >= 70:
                    color = "🟢 LIGHT GREEN"
                    risk = "LIKELY SAFE"
                else:
                    color = "🟢 LIGHT GREEN"
                    risk = "PROBABLY SAFE"
            
            print(f"🔍 {description}")
            print(f"   URL: {url}")
            print(f"   {color} - {risk}")
            print(f"   Prediction: {prediction.upper()}")
            print(f"   Confidence: {confidence}%")
            print()
            
        else:
            print(f"❌ Error testing {url}: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Failed to test {url}: {e}")

def main():
    """Test various URLs with different confidence levels"""
    print("🎨 PhishGuard Confidence Level Testing")
    print("=" * 50)
    print()
    
    # Test URLs with different confidence levels
    test_cases = [
        ("https://192.168.1.1/login", "Suspicious IP + Login (High Risk)"),
        ("https://www.bank-account-secure.com", "Suspicious Banking (High Risk)"),
        ("https://www.paypal-secure.com/login", "Fake PayPal (High Risk)"),
        ("https://suspicious-phishing-site.com", "Clearly Phishing (Very High Risk)"),
        ("https://www.google.com", "Legitimate Google (Safe)"),
        ("https://www.microsoft.com", "Legitimate Microsoft (Safe)"),
        ("https://legitimate-site.org", "Legitimate Organization (Safe)"),
        ("http://suspicious-site.com", "No HTTPS (Medium Risk)")
    ]
    
    for url, description in test_cases:
        test_url(url, description)
        print("-" * 40)
    
    print("🎯 Color Code Summary:")
    print("🔴 RED = Phishing Risk (Avoid)")
    print("🟢 GREEN = Safe (Proceed)")
    print("🟡 YELLOW = Uncertain (Use Caution)")

if __name__ == "__main__":
    main() 