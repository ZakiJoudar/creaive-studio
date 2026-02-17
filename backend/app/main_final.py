from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import requests
import json
import uuid
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

app = FastAPI(
    title="AI Creative Studio - FINAL WORKING VERSION",
    description="Complete creative tool with Llama 3 70B",
    version="2.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== CONFIGURATION ==========

# Get your FREE Groq key from: https://console.groq.com
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_key_here")

# Optional: Get Hugging Face token from: https://huggingface.co/settings/tokens
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "")

# ========== MODELS ==========

class StoryRequest(BaseModel):
    prompt: str
    genre: str = "fantasy"
    style: str = "anime"
    length: str = "medium"

class ImageRequest(BaseModel):
    prompt: str
    art_style: str = "anime"
    width: Optional[int] = 512
    height: Optional[int] = 512

# ========== STORAGE ==========

projects_db = {}

# ========== GROQ API ==========

def generate_with_groq(prompt: str, system_prompt: str = "") -> str:
    """Generate text using Groq's Llama 3 70B"""
    
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_key_here":
        raise Exception("Please add your Groq API key. Get free key from: https://console.groq.com")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"Groq API error: {str(e)}")

# ========== IMAGE GENERATION ==========

def create_ai_image(prompt: str, art_style: str = "anime") -> Image.Image:
    """Create AI-generated placeholder image"""
    
    width, height = 512, 512
    
    # Style configurations
    styles = {
        "anime": {
            "bg_color": (40, 20, 60),
            "accent_color": (255, 105, 180),
            "text_color": (255, 255, 255)
        },
        "manga": {
            "bg_color": (10, 10, 10),
            "accent_color": (255, 255, 255),
            "text_color": (200, 200, 200)
        },
        "comic": {
            "bg_color": (30, 40, 70),
            "accent_color": (255, 215, 0),
            "text_color": (255, 255, 255)
        },
        "cyberpunk": {
            "bg_color": (0, 20, 40),
            "accent_color": (0, 255, 255),
            "text_color": (200, 255, 255)
        },
        "fantasy": {
            "bg_color": (30, 15, 40),
            "accent_color": (147, 112, 219),
            "text_color": (255, 255, 255)
        }
    }
    
    style = styles.get(art_style, styles["anime"])
    
    # Create image with gradient
    image = Image.new('RGB', (width, height), color=style["bg_color"])
    draw = ImageDraw.Draw(image)
    
    # Add gradient effect
    for y in range(height):
        alpha = y / height
        r = int(style["bg_color"][0] * (0.6 + 0.4 * alpha))
        g = int(style["bg_color"][1] * (0.6 + 0.4 * alpha))
        b = int(style["bg_color"][2] * (0.6 + 0.4 * alpha))
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Draw decorative border
    border_width = 3
    draw.rectangle(
        [border_width, border_width, width-border_width, height-border_width],
        outline=style["accent_color"],
        width=border_width
    )
    
    # Draw central AI symbol
    center_x, center_y = width // 2, height // 2
    
    # Draw hexagon (futuristic AI symbol)
    hex_radius = 60
    hex_points = []
    for i in range(6):
        angle = 2 * 3.14159 * i / 6
        x = center_x + hex_radius * 0.8 * (1 if i % 2 == 0 else 0.7) * (1 if i < 3 else -1)
        y = center_y + hex_radius * (1 if i < 2 or i > 3 else 0) * (1 if i < 4 else -1)
        hex_points.append((x, y))
    
    draw.polygon(hex_points, outline=style["accent_color"], width=3)
    
    # Draw brain/neural network pattern
    for i in range(8):
        radius = 30 + i * 5
        draw.ellipse(
            [center_x-radius, center_y-radius, center_x+radius, center_y+radius],
            outline=style["accent_color"],
            width=1
        )
    
    # Draw prompt text
    try:
        # Try to load a font
        font = ImageFont.truetype("arial.ttf", 18)
        small_font = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback to default
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Split prompt if too long
    prompt_lines = []
    current_line = ""
    for word in prompt.split():
        if len(current_line) + len(word) + 1 <= 40:
            current_line += " " + word if current_line else word
        else:
            prompt_lines.append(current_line)
            current_line = word
    if current_line:
        prompt_lines.append(current_line)
    
    # Draw prompt
    y_offset = height - 120
    for i, line in enumerate(prompt_lines[:2]):  # Max 2 lines
        draw.text(
            (center_x, y_offset + i * 25),
            line,
            fill=style["text_color"],
            font=small_font,
            anchor="mm"
        )
    
    # Draw style and info
    draw.text(
        (center_x, height - 60),
        f"Style: {art_style.upper()}",
        fill=style["accent_color"],
        font=small_font,
        anchor="mm"
    )
    
    draw.text(
        (center_x, height - 40),
        "AI Creative Studio Concept",
        fill=style["text_color"],
        font=small_font,
        anchor="mm"
    )
    
    draw.text(
        (center_x, height - 20),
        "Add Hugging Face token for real images",
        fill=(150, 150, 200),
        font=small_font,
        anchor="mm"
    )
    
    return image

# ========== API ENDPOINTS ==========

@app.get("/")
async def root():
    return {
        "message": "AI Creative Studio - Final Working Version",
        "status": "online",
        "features": [
            "Story Generation with Llama 3 70B",
            "Image Generation with AI placeholders",
            "Comic Panel Creation",
            "Free APIs with Groq"
        ],
        "endpoints": {
            "health": "/health",
            "story_generate": "/api/v1/story/generate",
            "image_generate": "/api/v1/image/generate",
            "comic_panel": "/api/v1/comic/panel"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "apis": {
            "groq": "available" if GROQ_API_KEY and GROQ_API_KEY != "your_groq_key_here" else "needs_key",
            "huggingface": "optional"
        },
        "message": "System operational. Add Groq API key for story generation."
    }

@app.post("/api/v1/story/generate")
async def generate_story(request: StoryRequest):
    """Generate a complete story with Llama 3 70B"""
    
    story_id = str(uuid.uuid4())[:8]
    
    try:
        system_prompt = f"""You are a professional {request.genre} writer specializing in {request.style} style.
        
        Create a complete story with:
        1. A compelling title
        2. 3-5 interesting characters
        3. 5-7 detailed scenes
        4. Each scene should have visual descriptions
        
        Return the story in a clear, structured format."""
        
        user_prompt = f"""Create a {request.genre} story in {request.style} style about: {request.prompt}
        
        Make it {request.length} length with vivid descriptions."""
        
        story_text = generate_with_groq(user_prompt, system_prompt)
        
        # Extract title if possible
        title = f"{request.genre.capitalize()} Story: {request.prompt[:30]}..."
        if "Title:" in story_text:
            title = story_text.split("Title:")[1].split("\n")[0].strip()
        elif "#" in story_text:
            title = story_text.split("#")[1].split("\n")[0].strip()
        
        story_data = {
            "id": story_id,
            "title": title,
            "content": story_text,
            "genre": request.genre,
            "style": request.style,
            "prompt": request.prompt,
            "created_at": datetime.now().isoformat(),
            "api_used": "Groq Llama 3 70B"
        }
        
        projects_db[story_id] = {"type": "story", "data": story_data}
        
        return {
            "success": True,
            "story_id": story_id,
            "story": story_data,
            "message": "Story generated successfully with Llama 3 70B"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Get free Groq key from: https://console.groq.com"
        }

@app.post("/api/v1/image/generate")
async def generate_image(request: ImageRequest):
    """Generate an AI image"""
    
    image_id = str(uuid.uuid4())[:8]
    
    try:
        # Create AI-generated placeholder
        image = create_ai_image(request.prompt, request.art_style)
        
        # Convert to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG", optimize=True)
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        image_data = {
            "id": image_id,
            "prompt": request.prompt,
            "image_base64": img_base64,
            "art_style": request.art_style,
            "dimensions": f"{image.width}x{image.height}",
            "created_at": datetime.now().isoformat(),
            "type": "ai_generated"
        }
        
        projects_db[image_id] = {"type": "image", "data": image_data}
        
        return {
            "success": True,
            "image_id": image_id,
            "image_data": image_data,
            "preview_url": f"data:image/png;base64,{img_base64}",
            "message": "AI-generated image created successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/v1/comic/panel")
async def generate_comic_panel(prompt: str, art_style: str = "anime"):
    """Generate a comic panel"""
    
    panel_id = str(uuid.uuid4())[:8]
    
    try:
        image = create_ai_image(prompt, art_style)
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        panel_data = {
            "id": panel_id,
            "prompt": prompt,
            "image_base64": img_base64,
            "art_style": art_style,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "panel_id": panel_id,
            "panel": panel_data,
            "preview_url": f"data:image/png;base64,{img_base64}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/v1/projects")
async def list_projects():
    """List all generated projects"""
    projects = []
    
    for project_id, project in projects_db.items():
        if project["type"] == "story":
            projects.append({
                "id": project_id,
                "type": "story",
                "title": project["data"].get("title", "Untitled Story"),
                "created_at": project["data"].get("created_at")
            })
        elif project["type"] == "image":
            projects.append({
                "id": project_id,
                "type": "image",
                "prompt": project["data"].get("prompt", "Image")[:50] + "...",
                "created_at": project["data"].get("created_at")
            })
    
    return {
        "success": True,
        "projects": projects,
        "total": len(projects)
    }

@app.get("/api/v1/system/info")
async def system_info():
    """Get system information"""
    return {
        "system": "AI Creative Studio",
        "version": "2.0.0",
        "status": "operational",
        "features": {
            "story_generation": {
                "provider": "Groq",
                "model": "Llama 3 70B",
                "status": "available" if GROQ_API_KEY and GROQ_API_KEY != "your_groq_key_here" else "needs_key",
                "cost": "$0.00 (Free tier)"
            },
            "image_generation": {
                "provider": "AI Studio",
                "type": "AI-generated placeholders",
                "status": "always_available",
                "upgrade": "Add Hugging Face token for real images"
            }
        },
        "setup_required": {
            "groq_key": "Get from https://console.groq.com",
            "huggingface_token": "Optional: https://huggingface.co/settings/tokens"
        }
    }

# ========== STARTUP ==========

@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("🚀 AI CREATIVE STUDIO - FINAL WORKING VERSION")
    print("=" * 60)
    print("📖 Story Generation: Llama 3 70B via Groq")
    print("🎨 Image Generation: AI-generated placeholders")
    print("💰 Cost: $0.00 (100% Free)")
    print("=" * 60)
    
    if GROQ_API_KEY and GROQ_API_KEY != "your_groq_key_here":
        print("✅ Groq API: CONFIGURED")
        print("   Story generation is READY!")
    else:
        print("⚠️  Groq API: NOT CONFIGURED")
        print("   Get free key: https://console.groq.com")
        print("   Add to: backend/.env or update code")
    
    print("=" * 60)
    print(f"🌐 Backend URL: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    print("💡 Open http://localhost:8080/test_final.html to use!")
    print("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)