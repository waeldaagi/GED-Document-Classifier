#!/usr/bin/env python3
"""
Test script for the GED Navigation System
"""

import requests
import time
import webbrowser

def test_navigation_system():
    """Test the navigation system by checking all components"""
    
    print("🧭 Testing GED Navigation System")
    print("=" * 50)
    
    # Component URLs
    components = {
        "📄 Document Classifier": "http://localhost:8502",
        "📊 Analytics Dashboard": "http://localhost:8503", 
        "🔍 API Health": "http://localhost:8000/health"
    }
    
    results = {}
    
    for name, url in components.items():
        print(f"\n🔍 Testing {name}...")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name} is accessible")
                results[name] = "✅ Online"
            else:
                print(f"⚠️ {name} returned status {response.status_code}")
                results[name] = f"⚠️ Status {response.status_code}"
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} is not accessible")
            results[name] = "❌ Offline"
        except requests.exceptions.Timeout:
            print(f"⏰ {name} timed out")
            results[name] = "⏰ Timeout"
        except Exception as e:
            print(f"❌ {name} error: {e}")
            results[name] = f"❌ Error: {e}"
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 NAVIGATION SYSTEM TEST RESULTS")
    print("=" * 50)
    
    for name, status in results.items():
        print(f"{name}: {status}")
    
    # Count online components
    online_count = sum(1 for status in results.values() if "✅" in status)
    total_count = len(results)
    
    print(f"\n🎯 Overall Status: {online_count}/{total_count} components online")
    
    if online_count == total_count:
        print("🎉 All components are running! Navigation system is ready.")
        print("\n🌐 You can now:")
        print("1. Open http://localhost:8502 for Document Classifier")
        print("2. Open http://localhost:8503 for Analytics Dashboard") 
        print("3. Open http://localhost:8000/docs for API Documentation")
        print("4. Use the navigation sidebar in each app to switch between components")
        
        # Ask if user wants to open components
        try:
            choice = input("\n🚀 Would you like to open the Document Classifier in your browser? (y/n): ")
            if choice.lower() in ['y', 'yes']:
                webbrowser.open("http://localhost:8502")
                print("✅ Opening Document Classifier...")
        except:
            pass
            
    else:
        print("⚠️ Some components are not running. Check the logs above.")
    
    return online_count == total_count

if __name__ == "__main__":
    test_navigation_system()
