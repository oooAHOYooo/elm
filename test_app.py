#!/usr/bin/env python3
"""
Test script for Elm City Daily
Run this to verify all endpoints and functionality
"""
import sys
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(name, url, expected_status=200, check_content=None):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(url, timeout=10)
        status = response.status_code
        print(f"Status: {status}")
        
        if status != expected_status:
            print(f"❌ FAILED - Expected {expected_status}, got {status}")
            return False
        
        if check_content:
            if check_content not in response.text:
                print(f"❌ FAILED - Expected content '{check_content}' not found")
                return False
        
        print(f"✅ PASSED")
        
        # Show preview of response
        if response.headers.get('content-type', '').startswith('text/html'):
            preview = response.text[:200].replace('\n', ' ')
            print(f"Preview: {preview}...")
        elif response.headers.get('content-type', '').startswith('application/json'):
            try:
                data = response.json()
                print(f"JSON keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
            except:
                print(f"Preview: {response.text[:200]}")
        elif response.headers.get('content-type', '').startswith('application/rss+xml'):
            print(f"RSS Feed detected - {len(response.text)} bytes")
            if '<rss' in response.text and '<channel>' in response.text:
                print("✅ Valid RSS structure")
            else:
                print("❌ Invalid RSS structure")
                return False
        else:
            preview = response.text[:200]
            print(f"Preview: {preview}...")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ FAILED - Could not connect to {BASE_URL}")
        print("   Make sure the Flask app is running: python app.py")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ FAILED - Request timed out")
        return False
    except Exception as e:
        print(f"❌ FAILED - Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("ELM CITY DAILY - TEST SUITE")
    print("="*60)
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Homepage", f"{BASE_URL}/", 200, "Elm City Daily"),
        ("About Page", f"{BASE_URL}/about", 200, "Elm City"),
        ("Feeds API (JSON)", f"{BASE_URL}/feeds", 200, None),
        ("RSS Feed", f"{BASE_URL}/feeds.rss", 200, None),
        ("NWS Alerts API", f"{BASE_URL}/api/nws/alerts", 200, None),
        ("Tides API", f"{BASE_URL}/api/tides", 200, None),
        ("Events Week API", f"{BASE_URL}/api/events/week", 200, None),
        ("Events Week API (offset)", f"{BASE_URL}/api/events/week?offset=1", 200, None),
    ]
    
    results = []
    for name, url, status, content in tests:
        result = test_endpoint(name, url, status, content)
        results.append((name, result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
