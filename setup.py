#!/usr/bin/env python3
import os
import subprocess
import sys

def setup_project():
    print("🚀 Setting up AI Creative Studio...")
    print("=" * 60)
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return
    
    print("✅ Python version check passed")
    
    # Create necessary directories
    directories = [
        "backend/app/api/v1/endpoints",
        "backend/app/core",
        "backend/app/models",
        "backend/app/services",
        "backend/app/utils",
        "frontend/css",
        "frontend/js",
        "frontend/lib"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directory structure created")
    
    # Install backend dependencies
    print("\n📦 Installing backend dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"])
        print("✅ Backend dependencies installed")
    except subprocess.CalledProcessError:
        print("⚠️  Could not install dependencies automatically")
        print("   Please run: pip install -r backend/requirements.txt")
    
    # Create .env file if it doesn't exist
    env_file = "backend/.env"
    if not os.path.exists(env_file):
        with open(env_file, "w") as f:
            f.write("""# API Keys (Get from below URLs)
GROQ_API_KEY=your_groq_key_here
HUGGINGFACE_API_KEY=your_hf_token_here

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Model Defaults
DEFAULT_LLM_MODEL=llama3-70b-8192
DEFAULT_IMAGE_MODEL=stabilityai/stable-diffusion-xl-base-1.0
""")
        print("✅ Created .env file")
    
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Get FREE API keys:")
    print("   • Groq: https://console.groq.com")
    print("   • Hugging Face: https://huggingface.co/settings/tokens")
    print("\n2. Update backend/.env with your API keys")
    print("\n3. Start the backend:")
    print("   cd backend")
    print("   uvicorn app.main:app --reload --port 8000")
    print("\n4. Start the frontend:")
    print("   cd frontend")
    print("   python -m http.server 8080")
    print("\n5. Open browser:")
    print("   http://localhost:8080")
    print("\n6. Generate your first story! 🚀")

if __name__ == "__main__":
    setup_project()