#!/usr/bin/env python3
"""
Simple setup script for AI Creative Studio
"""

import os
import sys
import json
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import google.generativeai
        import fastapi
        import sqlalchemy
        print("✓ Required packages are installed")
    except ImportError as e:
        print(f"✗ Missing package: {e}")
        print("Run: pip install -r requirements.txt")
        return False
    return True

def setup_environment():
    """Setup environment variables"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("Creating .env file...")
        
        gemini_key = input("Enter your Gemini API key (press Enter to skip): ").strip()
        
        env_content = f"""# AI Creative Studio Environment Variables

# Gemini API (required for full functionality)
GEMINI_API_KEY={gemini_key or 'your_gemini_key_here'}

# Optional HuggingFace token for image generation
# HUGGINGFACE_TOKEN=your_token_here

# Security
SECRET_KEY=dev-secret-key-change-in-production

# Local development settings
DATABASE_URL=sqlite+aiosqlite:///./creative_studio.db
"""
        
        env_file.write_text(env_content)
        print("✓ Created .env file")
    else:
        print("✓ .env file already exists")
    
    # Create generated assets directory
    assets_dir = Path("./generated_assets")
    assets_dir.mkdir(exist_ok=True)
    print("✓ Created generated_assets directory")
    
    return True

def initialize_database():
    """Initialize SQLite database"""
    try:
        # Import after environment is set
        from app.core.database import engine, Base
        import asyncio
        
        async def init_db():
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        
        asyncio.run(init_db())
        print("✓ Database initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

def main():
    print("=" * 50)
    print("AI Creative Studio Setup")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print("\n1. Checking requirements...")
    if not check_requirements():
        sys.exit(1)
    
    print("\n2. Setting up environment...")
    if not setup_environment():
        sys.exit(1)
    
    print("\n3. Initializing database...")
    if not initialize_database():
        print("Warning: Database initialization failed, but setup can continue")
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the backend server:")
    print("   uvicorn app.main:app --reload --port 8000")
    print("\n2. Start the frontend server:")
    print("   cd ../frontend && python -m http.server 8080")
    print("\n3. Open your browser:")
    print("   http://localhost:8080")
    print("\n4. (Optional) Start Redis for background tasks:")
    print("   docker run -d -p 6379:6379 redis:7-alpine")
    print("=" * 50)

if __name__ == "__main__":
    main()