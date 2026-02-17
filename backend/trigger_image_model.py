import requests
import time

print("🔄 Triggering Hugging Face model load...")
print("This will take 30-60 seconds on first request")
print("=" * 50)

try:
    # Simple test request to load the model
    payload = {
        "prompt": "A cat, anime style",
        "art_style": "anime"
    }
    
    print("Sending request to load model...")
    response = requests.post(
        "http://localhost:8000/api/v1/image/generate",
        json=payload,
        timeout=120  # 2 minute timeout for first load
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ Model loaded successfully!")
            print(f"Image generated: {result.get('image_id')}")
        else:
            print(f"⚠️ Response: {result.get('message', 'Model loading...')}")
    else:
        print(f"❌ Status: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("⚠️ Request timed out (normal for first load)")
    print("The model is now loading in background")
    print("Next requests will be faster!")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("💡 Now test image generation in browser:")
print("http://localhost:8080/test_api.html")
print("=" * 50)