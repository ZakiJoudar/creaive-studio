import requests
import json

print("=" * 60)
print("🧪 QUICK API TEST")
print("=" * 60)

# Test 1: Health check
print("\n1. Testing backend health...")
try:
    resp = requests.get("http://localhost:8000/health", timeout=5)
    health = resp.json()
    print(f"✅ Backend: {health.get('backend', 'unknown')}")
    print(f"   Groq: {health.get('apis', {}).get('groq', {}).get('status', 'unknown')}")
    print(f"   Hugging Face: {health.get('apis', {}).get('huggingface', {}).get('status', 'unknown')}")
except Exception as e:
    print(f"❌ Health check failed: {e}")
    exit()

# Test 2: Quick story generation
print("\n2. Testing story generation...")
try:
    payload = {
        "prompt": "A friendly robot exploring ancient ruins",
        "genre": "adventure",
        "style": "anime"
    }
    
    resp = requests.post("http://localhost:8000/api/v1/story/generate", 
                        json=payload, timeout=30)
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get("success"):
            print("✅ Story generation: WORKING!")
            print(f"   Title: {result.get('story', {}).get('title', 'Unknown')}")
            print(f"   Characters: {result.get('details', {}).get('characters_count', 0)}")
            print(f"   Scenes: {result.get('details', {}).get('scenes_count', 0)}")
        else:
            print("❌ Story generation failed")
            print(f"   Error: {result.get('error')}")
            print(f"   Message: {result.get('message')}")
    else:
        print(f"❌ API error: {resp.status_code}")
        
except Exception as e:
    print(f"❌ Test failed: {e}")

print("\n" + "=" * 60)
print("🎯 If story generation works, your Groq API key is correct!")
print("=" * 60)