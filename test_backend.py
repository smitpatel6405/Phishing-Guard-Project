#!/usr/bin/env python3
"""
Test script for PhishGuard Flask backend
Tests the API endpoints and feature extraction functionality
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:5000"
TEST_URLS = [
    "https://www.google.com",
    "http://suspicious-site.com",
    "https://192.168.1.1/login",
    "https://www.bank-account-secure.com/update",
    "https://legitimate-site.org"
]

def test_health_endpoint():
    """Test the health check endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False

def test_home_endpoint():
    """Test the home endpoint"""
    print("\n🔍 Testing home endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Home endpoint: {data['message']}")
            return True
        else:
            print(f"❌ Home endpoint failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Home endpoint error: {e}")
        return False

def test_predict_endpoint(url):
    """Test the prediction endpoint with a specific URL"""
    print(f"\n🔍 Testing prediction for: {url}")
    try:
        payload = {"url": url}
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction successful:")
            print(f"   URL: {data['url']}")
            print(f"   Prediction: {data['prediction']}")
            print(f"   Confidence: {data['confidence']}%")
            
            # Display features
            if 'features' in data:
                print("   Features:")
                for key, value in data['features'].items():
                    print(f"     {key}: {value}")
            return True
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Prediction error: {e}")
        return False

def test_invalid_requests():
    """Test invalid request handling"""
    print("\n🔍 Testing invalid request handling...")
    
    # Test missing URL
    try:
        payload = {}
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        if response.status_code == 400:
            print("✅ Missing URL handled correctly")
        else:
            print(f"❌ Missing URL not handled correctly: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Missing URL test error: {e}")
    
    # Test empty URL
    try:
        payload = {"url": ""}
        response = requests.post(
            f"{BASE_URL}/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        if response.status_code == 400:
            print("✅ Empty URL handled correctly")
        else:
            print(f"❌ Empty URL not handled correctly: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Empty URL test error: {e}")

def run_performance_test():
    """Run a simple performance test"""
    print("\n🔍 Running performance test...")
    
    test_url = "https://www.example.com"
    times = []
    
    for i in range(5):
        start_time = time.time()
        try:
            payload = {"url": test_url}
            response = requests.post(
                f"{BASE_URL}/predict",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                times.append(response_time)
                print(f"   Request {i+1}: {response_time:.2f}ms")
            else:
                print(f"   Request {i+1}: Failed")
        except requests.exceptions.RequestException as e:
            print(f"   Request {i+1}: Error - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"✅ Average response time: {avg_time:.2f}ms")
    else:
        print("❌ No successful requests for performance test")

def main():
    """Main test function"""
    print("🚀 Starting PhishGuard Backend Tests")
    print("=" * 50)
    
    # Check if backend is running
    print("🔍 Checking if backend is running...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running!")
        else:
            print("❌ Backend responded but with error")
            return
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not running: {e}")
        print("💡 Please start the Flask backend with: python app.py")
        return
    
    # Run tests
    test_health_endpoint()
    test_home_endpoint()
    
    # Test predictions for various URLs
    for url in TEST_URLS:
        test_predict_endpoint(url)
    
    test_invalid_requests()
    run_performance_test()
    
    print("\n" + "=" * 50)
    print("🎉 Backend tests completed!")
    print("\n💡 To test the Chrome extension:")
    print("   1. Load the extension in Chrome")
    print("   2. Navigate to different websites")
    print("   3. Check the extension popup for results")

if __name__ == "__main__":
    main() 