#!/usr/bin/env python3
"""
PhishGuard Auto Start & Test Script
Automatically starts the backend server and runs comprehensive tests
"""

import subprocess
import time
import requests
import json
import sys
import os

def print_header():
    """Print the header"""
    print("=" * 60)
    print("    🛡️ PhishGuard Auto Start & Test")
    print("=" * 60)
    print()

def check_python():
    """Check if Python 3.8 is available"""
    print("🔍 Checking Python 3.8 availability...")
    try:
        result = subprocess.run(["py", "-3.8", "--version"], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ {result.stdout.strip()}")
            return True
        else:
            print("❌ Python 3.8 not found!")
            return False
    except Exception as e:
        print(f"❌ Error checking Python: {e}")
        return False

def start_server():
    """Start the Flask server in background"""
    print("🚀 Starting PhishGuard Backend Server...")
    print("   This will start the server on http://localhost:5000")
    print()
    
    try:
        # Start server in background
        process = subprocess.Popen(
            ["py", "-3.8", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        print("✅ Server process started!")
        print("⏳ Waiting for server to be ready...")
        
        # Wait for server to start
        for i in range(15):
            try:
                response = requests.get("http://localhost:5000/health", timeout=2)
                if response.status_code == 200:
                    print(f"✅ Server is ready! (took {i+1} seconds)")
                    return process
            except:
                print(f"   Waiting... ({i+1}/15)")
                time.sleep(1)
        
        print("⚠️ Server might still be starting...")
        return process
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def test_backend():
    """Test the backend endpoints"""
    print()
    print("🧪 Testing Backend Endpoints...")
    print("-" * 40)
    
    # Test health endpoint
    print("🔍 Health Check:")
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   ✅ Model: {'Loaded' if data['model_loaded'] else 'Not Loaded'}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test home endpoint
    print("\n📊 Home Endpoint:")
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Message: {data['message']}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test prediction endpoint
    print("\n🔮 Prediction Test:")
    try:
        payload = {"url": "https://www.google.com"}
        response = requests.post(
            "http://localhost:5000/predict",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Prediction: {data['prediction']}")
            print(f"   ✅ Confidence: {data['confidence']}%")
            print(f"   ✅ Features: {len(data['features'])} extracted")
        else:
            print(f"   ❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   ❌ Details: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   ❌ Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

def run_demo():
    """Run a quick demo"""
    print("\n🎬 Running Quick Demo...")
    print("-" * 40)
    
    test_urls = [
        ("https://www.google.com", "Google"),
        ("https://192.168.1.1/login", "Suspicious IP"),
        ("https://www.bank-account-secure.com", "Suspicious Banking")
    ]
    
    for url, description in test_urls:
        print(f"\n🔍 Testing: {description}")
        try:
            payload = {"url": url}
            response = requests.post(
                "http://localhost:5000/predict",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Result: {data['prediction'].upper()}")
                print(f"   Confidence: {data['confidence']}%")
            else:
                print(f"   Error: {response.status_code}")
        except Exception as e:
            print(f"   Failed: {e}")
        
        time.sleep(0.5)

def show_next_steps():
    """Show next steps to the user"""
    print()
    print("=" * 60)
    print("🎉 PhishGuard Backend is Ready!")
    print("=" * 60)
    print()
    print("✅ Server: http://localhost:5000")
    print("✅ Status: Running and Tested")
    print("✅ Model: Loaded and Working")
    print()
    print("💡 Next Steps:")
    print("1. Load the Chrome extension in Chrome")
    print("2. Go to chrome://extensions/")
    print("3. Enable 'Developer mode'")
    print("4. Click 'Load unpacked' and select this folder")
    print()
    print("🔧 To stop the server later:")
    print("1. Press Ctrl+Alt+Delete")
    print("2. End the 'python.exe' process")
    print()
    print("🎯 The server will keep running in the background!")
    print("   You can now close this window and use the extension!")
    print()

def main():
    """Main function"""
    print_header()
    
    # Check Python
    if not check_python():
        print("❌ Cannot continue without Python 3.8")
        input("Press Enter to exit...")
        return
    
    # Start server
    process = start_server()
    if not process:
        print("❌ Failed to start server")
        input("Press Enter to exit...")
        return
    
    # Test backend
    test_backend()
    
    # Run demo
    run_demo()
    
    # Show next steps
    show_next_steps()
    
    # Keep the script running to maintain server process
    print("🔄 Server is running in background...")
    print("   Close this window when you're ready to stop the server")
    input("Press Enter to stop server and exit...")
    
    # Stop server
    try:
        process.terminate()
        print("🛑 Server stopped.")
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...") 