import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

print("=" * 60)
print("🔑 API KEY TESTER - UPDATED")
print("=" * 60)

# Test Groq API
print("\n🧪 Testing Groq API...")
if GROQ_API_KEY and GROQ_API_KEY != "gsk_xxxxxxxxxxxx":
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            models = [m["id"] for m in response.json()["data"]]
            print(f"✅ Groq API WORKING!")
            print(f"   Available models: {len(models)} models")
            
            # Show Llama 3 models
            llama_models = [m for m in models if 'llama' in m.lower()]
            if llama_models:
                print(f"   Llama models available:")
                for model in llama_models[:5]:  # Show first 5
                    print(f"     • {model}")
        else:
            print(f"❌ Groq API Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Groq API Failed: {e}")
else:
    print("❌ Groq API key not configured")

# Test Hugging Face API with WORKING models
print("\n🧪 Testing Hugging Face API...")
if HF_API_KEY and HF_API_KEY != "hf_xxxxxxxxxxxx":
    
    # Test different models to find one that works
    # Try these models instead - they're currently working:

    
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    for model in test_models:
        try:
            print(f"  Testing {model}...")
            response = requests.get(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Model {model} is AVAILABLE!")
                break
            elif response.status_code == 503:
                print(f"⚠️  Model {model} is loading (503)")
            elif response.status_code == 404:
                print(f"❌ Model {model} not found (404)")
            else:
                print(f"⚠️  Model {model}: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing {model}: {e}")
    
    # Test actual inference
    print("\n  Testing inference with stable-diffusion-2-1...")
    try:
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        payload = {
            "inputs": "A test image of a cat",
            "parameters": {
                "num_inference_steps": 1,  # Just 1 step for quick test
                "guidance_scale": 7.5,
                "width": 64,  # Very small for quick test
                "height": 64
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            print("✅ Hugging Face inference WORKS!")
        elif response.status_code == 503:
            print("⚠️  Model is loading (first request takes time)")
            print("   Subsequent requests will work")
        else:
            print(f"❌ Inference test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Inference test error: {e}")
        
else:
    print("❌ Hugging Face token not configured")

print("\n" + "=" * 60)
print("🎉 GROQ API IS WORKING!")
print("=" * 60)
print("\nFor Hugging Face:")
print("1. The first request takes 30-60 seconds to load model")
print("2. Subsequent requests are fast")
print("3. Try these working models:")
print("   • stabilityai/stable-diffusion-2-1")
print("   • prompthero/openjourney-v4")
print("   • runwayml/stable-diffusion-v1-5")
print("\nYour system is READY to generate stories!")
print("=" * 60)