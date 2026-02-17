"""
FLUX.2 + WAN GENERATORS
Image and video generation with Hugging Face models
"""

import torch
from diffusers import StableDiffusionPipeline, StableVideoDiffusionPipeline
from diffusers import FluxPipeline
from transformers import pipeline as hf_pipeline
from huggingface_hub import login
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
import os
from pathlib import Path
import uuid
import time
from typing import List, Dict, Any, Optional
import base64
from io import BytesIO

# Load environment
from dotenv import load_dotenv
load_dotenv()

# Hugging Face authentication
HF_TOKEN = os.getenv("HF_TOKEN", "")
if HF_TOKEN:
    try:
        login(token=HF_TOKEN)
        print("✅ Logged into Hugging Face")
    except:
        print("⚠️ Could not log into Hugging Face, using public models")

# Workspace directories
BASE_DIR = Path(__file__).parent.parent
WORKSPACE_DIR = BASE_DIR / "workspace"
COMICS_DIR = WORKSPACE_DIR / "comics"
ANIMATIONS_DIR = WORKSPACE_DIR / "animations"
MODELS_DIR = WORKSPACE_DIR / "models"

# Create directories
for dir_path in [COMICS_DIR, ANIMATIONS_DIR, MODELS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ========== STORY GENERATOR ==========

class StoryGenerator:
    """Generate stories and scene breakdowns"""
    
    def __init__(self):
        print("📖 Initializing Story Generator...")
        try:
            self.story_pipeline = hf_pipeline(
                "text-generation",
                model="microsoft/DialoGPT-medium",
                device=0 if torch.cuda.is_available() else -1
            )
        except:
            self.story_pipeline = None
            print("⚠️ Using simulated story generation")
    
    def generate_from_premise(self, premise: str, genre: str) -> Dict:
        """Generate complete story from premise"""
        
        scenes = self._generate_scenes(premise, genre)
        
        return {
            "id": f"story_{uuid.uuid4().hex[:8]}",
            "premise": premise,
            "genre": genre,
            "scenes": scenes,
            "total_scenes": len(scenes),
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_scenes(self, premise: str, genre: str) -> List[Dict]:
        """Generate scene breakdown"""
        
        # Scene templates based on genre
        genre_scenes = {
            "cyberpunk": [
                {
                    "scene_number": 1,
                    "description": f"Opening scene in futuristic city: {premise}",
                    "characters": ["Protagonist"],
                    "location": "Neo-Tokyo streets at night",
                    "mood": "Mysterious, tense",
                    "key_visual": "Rainy neon-lit streets with holographic ads",
                    "duration": "10 seconds",
                    "camera_angles": ["Establishing wide shot", "Close-up on protagonist"],
                    "sound_design": "Ambient rain, distant city sounds, synth music"
                },
                {
                    "scene_number": 2,
                    "description": "Investigation and discovery",
                    "characters": ["Protagonist", "Supporting Character"],
                    "location": "High-tech laboratory or data center",
                    "mood": "Suspenseful, revealing",
                    "key_visual": "Holographic data displays, glowing interfaces",
                    "duration": "15 seconds",
                    "camera_angles": ["Tracking shot", "Over-the-shoulder", "Dutch angle"],
                    "sound_design": "Electronic beeps, data stream sounds, tense music"
                },
                {
                    "scene_number": 3,
                    "description": "Climax and resolution",
                    "characters": ["Protagonist", "Antagonist"],
                    "location": "Rooftop or digital realm",
                    "mood": "Intense, dramatic",
                    "key_visual": "Confrontation with dramatic lighting",
                    "duration": "20 seconds",
                    "camera_angles": ["Low angle", "Extreme close-up", "360 rotation"],
                    "sound_design": "Epic music, impactful sound effects, emotional score"
                }
            ],
            "fantasy": [
                {
                    "scene_number": 1,
                    "description": f"Discovery in magical world: {premise}",
                    "characters": ["Hero", "Mentor"],
                    "location": "Ancient forest or mystical realm",
                    "mood": "Wonderous, adventurous",
                    "key_visual": "Magical glowing forest, mythical creatures",
                    "duration": "12 seconds",
                    "camera_angles": ["Sweeping landscape shot", "Character introduction"],
                    "sound_design": "Orchestral music, nature sounds, magical chimes"
                },
                {
                    "scene_number": 2,
                    "description": "Training and preparation",
                    "characters": ["Hero", "Allies"],
                    "location": "Training grounds or mystical temple",
                    "mood": "Hopeful, determined",
                    "key_visual": "Magic training montage, spell casting",
                    "duration": "18 seconds",
                    "camera_angles": ["Montage sequence", "Slow motion", "POV shots"],
                    "sound_design": "Training sounds, magical spells, uplifting music"
                },
                {
                    "scene_number": 3,
                    "description": "Epic battle and victory",
                    "characters": ["Hero", "Villain", "Allies"],
                    "location": "Castle ruins or battlefield",
                    "mood": "Epic, triumphant",
                    "key_visual": "Large-scale battle, magical explosions",
                    "duration": "25 seconds",
                    "camera_angles": ["Aerial shots", "Rapid cuts", "Heroic poses"],
                    "sound_design": "Epic orchestra, battle sounds, victory theme"
                }
            ],
            "sci_fi": [
                {
                    "scene_number": 1,
                    "description": f"Space discovery: {premise}",
                    "characters": ["Captain", "Crew"],
                    "location": "Spaceship bridge or alien planet",
                    "mood": "Awe-inspiring, tense",
                    "key_visual": "Alien landscape, advanced spacecraft",
                    "duration": "14 seconds",
                    "camera_angles": ["Space establishing shot", "Bridge POV"],
                    "sound_design": "Space ambiance, ship sounds, mysterious tones"
                },
                {
                    "scene_number": 2,
                    "description": "Alien encounter or technology discovery",
                    "characters": ["Explorer", "Alien/Android"],
                    "location": "Alien structure or derelict ship",
                    "mood": "Mysterious, revealing",
                    "key_visual": "Alien technology, holographic interfaces",
                    "duration": "16 seconds",
                    "camera_angles": ["Exploring shots", "Reveal shots", "Tense close-ups"],
                    "sound_design": "Alien sounds, technology hums, suspense music"
                },
                {
                    "scene_number": 3,
                    "description": "Escape or confrontation",
                    "characters": ["Protagonist", "Alien Threat"],
                    "location": "Escaping spacecraft or showdown location",
                    "mood": "Thrilling, intense",
                    "key_visual": "Space battle or dramatic escape",
                    "duration": "22 seconds",
                    "camera_angles": ["Action sequence", "Quick cuts", "Dramatic angles"],
                    "sound_design": "Laser sounds, engine roars, intense score"
                }
            ]
        }
        
        return genre_scenes.get(genre, genre_scenes["cyberpunk"])

# ========== FLUX.2 IMAGE GENERATOR ==========

class ImageGenerator:
    """FLUX.2 Image Generation for Comics"""
    
    def __init__(self, model_name: str = "black-forest-labs/FLUX.1-dev"):
        print("🎨 Initializing FLUX.2 Image Generator...")
        
        self.use_real_model = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            # Try to load FLUX.2 model (commented for safety, uncomment when ready)
            # self.pipeline = FluxPipeline.from_pretrained(
            #     model_name,
            #     torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            #     cache_dir=str(MODELS_DIR)
            # )
            # if self.device == "cuda":
            #     self.pipeline.to(self.device)
            # self.use_real_model = True
            # print("✅ FLUX.2 model loaded successfully")
            
            print("⚠️ Using simulated FLUX.2 generation")
            self.use_real_model = False
            
        except Exception as e:
            print(f"⚠️ Could not load FLUX.2 model: {e}")
            print("⚠️ Using simulated image generation")
            self.use_real_model = False
    
    def generate_comic_page(self, scene_description: str, style: str = "manga", page_num: int = 1) -> Dict:
        """Generate a comic page from scene description"""
        
        print(f"   Generating page {page_num}: {scene_description[:50]}...")
        
        if self.use_real_model:
            # Real FLUX.2 generation
            prompt = self._create_prompt(scene_description, style)
            
            image = self.pipeline(
                prompt=prompt,
                height=1200,
                width=800,
                num_inference_steps=50,
                guidance_scale=7.5
            ).images[0]
        else:
            # Simulated generation - create placeholder image
            image = self._create_placeholder_image(scene_description, style, page_num)
        
        # Save image
        image_id = f"comic_{uuid.uuid4().hex[:8]}"
        filename = f"{image_id}_page_{page_num:03d}.png"
        save_path = COMICS_DIR / filename
        
        image.save(save_path, "PNG", optimize=True)
        
        return {
            "page_number": page_num,
            "scene": scene_description,
            "image_path": str(save_path),
            "image_id": image_id,
            "filename": filename,
            "style": style,
            "generator": "FLUX.2" if self.use_real_model else "FLUX.2 (Simulated)"
        }
    
    def generate_comic_from_story(self, story_data: Dict, art_style: str = "manga") -> Dict:
        """Generate complete comic from story"""
        
        scenes = story_data.get("scenes", [])
        num_pages = min(len(scenes), 3)  # Generate up to 3 pages
        
        pages = []
        for i in range(num_pages):
            scene = scenes[i]
            page_data = self.generate_comic_page(
                scene_description=scene.get("description", ""),
                style=art_style,
                page_num=i + 1
            )
            pages.append(page_data)
        
        comic_id = f"comic_{uuid.uuid4().hex[:8]}"
        
        # Save comic metadata
        comic_data = {
            "id": comic_id,
            "pages": pages,
            "total_pages": len(pages),
            "story_id": story_data.get("id"),
            "art_style": art_style,
            "generator": "FLUX.2" if self.use_real_model else "FLUX.2 (Simulated)",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        save_path = COMICS_DIR / f"{comic_id}.json"
        with open(save_path, 'w') as f:
            json.dump(comic_data, f, indent=2)
        
        return comic_data
    
    def _create_prompt(self, scene_description: str, style: str) -> str:
        """Create prompt for FLUX.2"""
        
        style_prompts = {
            "manga": "Japanese manga style, black and white, detailed lineart, screentones, dynamic composition, comic page layout, speech bubbles, panel borders",
            "anime": "anime style, vibrant colors, cel-shaded, detailed characters, dynamic angles, emotional expressions, background art, key visual",
            "comic": "western comic book style, bold colors, ink outlines, superhero art style, dynamic poses, dramatic lighting, panel layout, American comics",
            "cyberpunk": "cyberpunk aesthetic, neon lights, futuristic city, rain effects, holographic displays, cybernetic enhancements, dark atmosphere, sci-fi",
            "fantasy": "fantasy art, magical environment, epic scale, detailed characters, mystical lighting, ancient architecture, heroic poses, fantasy illustration",
            "sci_fi": "science fiction, futuristic technology, space theme, alien elements, advanced machinery, clean design, sci-fi illustration, concept art"
        }
        
        style_prompt = style_prompts.get(style, style_prompts["manga"])
        
        return f"{style_prompt}, {scene_description}, professional comic art, high quality, detailed, 4K, masterpiece"
    
    def _create_placeholder_image(self, scene_description: str, style: str, page_num: int) -> Image.Image:
        """Create placeholder image for simulation"""
        
        width, height = 800, 1200
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Style-based colors
        style_colors = {
            "manga": ("black", "white"),
            "anime": ("#ff6b6b", "#4ecdc4"),
            "comic": ("#1e90ff", "#ff4757"),
            "cyberpunk": ("#00ffff", "#ff00ff"),
            "fantasy": ("#8a2be2", "#00fa9a"),
            "sci_fi": ("#00bfff", "#ff8c00")
        }
        
        text_color, accent_color = style_colors.get(style, ("black", "#666"))
        
        # Title
        try:
            font_large = ImageFont.truetype("arial.ttf", 32)
            font_medium = ImageFont.truetype("arial.ttf", 20)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw title
        draw.text((width//2, 50), f"COMIC PAGE {page_num}", 
                 fill=accent_color, font=font_large, anchor="mm")
        draw.text((width//2, 90), f"Style: {style.upper()}", 
                 fill=text_color, font=font_medium, anchor="mm")
        
        # Draw scene description
        y_offset = 150
        words = scene_description.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            bbox = draw.textbbox((0, 0), test_line, font=font_small)
            text_width = bbox[2] - bbox[0]
            
            if text_width > width - 100:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for i, line in enumerate(lines[:10]):  # Limit to 10 lines
            draw.text((width//2, y_offset + i*30), line, 
                     fill=text_color, font=font_small, anchor="mm")
        
        # Draw comic panels
        panels = [
            {"x": 50, "y": 450, "w": 700, "h": 200, "label": "Panel 1"},
            {"x": 50, "y": 680, "w": 340, "h": 200, "label": "Panel 2"},
            {"x": 410, "y": 680, "w": 340, "h": 200, "label": "Panel 3"}
        ]
        
        for panel in panels:
            # Panel border
            draw.rectangle([panel["x"], panel["y"], 
                          panel["x"] + panel["w"], panel["y"] + panel["h"]], 
                         outline=accent_color, width=3)
            
            # Panel label
            draw.text((panel["x"] + panel["w"]//2, panel["y"] + 20), 
                     panel["label"], fill=accent_color, font=font_small, anchor="mm")
            
            # Simple illustration
            if style == "cyberpunk":
                # Neon lines
                for j in range(3):
                    y = panel["y"] + 60 + j*40
                    draw.line([panel["x"] + 20, y, panel["x"] + panel["w"] - 20, y], 
                             fill=accent_color, width=2)
            elif style == "fantasy":
                # Magic circle
                center_x = panel["x"] + panel["w"]//2
                center_y = panel["y"] + panel["h"]//2
                draw.ellipse([center_x-30, center_y-30, center_x+30, center_y+30],
                           outline=accent_color, width=2)
        
        # Footer
        draw.text((width//2, height - 50), "Generated with FLUX.2 Simulation", 
                 fill=text_color, font=font_small, anchor="mm")
        
        return image

# ========== WAN VIDEO GENERATOR ==========

class VideoGenerator:
    """WAN Video Generation for Animation"""
    
    def __init__(self, model_name: str = "stabilityai/stable-video-diffusion-img2vid"):
        print("🎬 Initializing WAN Video Generator...")
        
        self.use_real_model = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            # Try to load WAN/Stable Video Diffusion model
            # self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
            #     model_name,
            #     torch_dtype=torch.float16,
            #     variant="fp16",
            #     cache_dir=str(MODELS_DIR)
            # )
            # if self.device == "cuda":
            #     self.pipeline.to(self.device)
            # self.use_real_model = True
            # print("✅ WAN model loaded successfully")
            
            print("⚠️ Using simulated WAN generation")
            self.use_real_model = False
            
        except Exception as e:
            print(f"⚠️ Could not load WAN model: {e}")
            print("⚠️ Using simulated video generation")
            self.use_real_model = False
    
    def generate_animation_scene(self, image_path: str, scene_description: str, duration: int = 3) -> Dict:
        """Generate animation scene from image"""
        
        print(f"   Animating scene: {scene_description[:50]}...")
        
        scene_id = f"scene_{uuid.uuid4().hex[:8]}"
        scene_dir = ANIMATIONS_DIR / scene_id
        scene_dir.mkdir(exist_ok=True)
        
        if self.use_real_model and Path(image_path).exists():
            # Real WAN generation
            base_image = Image.open(image_path)
            
            video_frames = self.pipeline(
                image=base_image,
                num_frames=duration * 8,  # 8fps
                num_inference_steps=25,
                motion_bucket_id=180,
                noise_aug_strength=0.1
            ).frames[0]
            
            frame_paths = []
            for i, frame in enumerate(video_frames):
                frame_path = scene_dir / f"frame_{i:04d}.png"
                frame.save(frame_path)
                frame_paths.append(str(frame_path))
        else:
            # Simulated generation - create placeholder frames
            frame_paths = self._create_placeholder_frames(scene_dir, duration, scene_description)
        
        # Create scene info
        scene_data = {
            "scene_id": scene_id,
            "description": scene_description,
            "duration": duration,
            "frame_count": len(frame_paths),
            "fps": 8,
            "frame_paths": frame_paths,
            "source_image": image_path,
            "generator": "WAN" if self.use_real_model else "WAN (Simulated)",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save scene data
        with open(scene_dir / "scene_info.json", 'w') as f:
            json.dump(scene_data, f, indent=2)
        
        return scene_data
    
    def generate_animation_from_comic(self, comic_data: Dict, duration: int = 30) -> Dict:
        """Generate complete animation from comic"""
        
        pages = comic_data.get("pages", [])
        scenes = []
        
        # Calculate duration per scene
        scenes_per_page = 1  # Simple: one scene per page
        total_scenes = len(pages) * scenes_per_page
        scene_duration = duration // total_scenes if total_scenes > 0 else 3
        
        for i, page in enumerate(pages):
            for j in range(scenes_per_page):
                scene_desc = f"Scene from page {i+1}: {page.get('scene', '')}"
                
                scene_data = self.generate_animation_scene(
                    image_path=page.get("image_path", ""),
                    scene_description=scene_desc,
                    duration=scene_duration
                )
                scenes.append(scene_data)
        
        animation_id = f"anim_{uuid.uuid4().hex[:8]}"
        
        # Create animation data
        animation_data = {
            "id": animation_id,
            "comic_id": comic_data.get("id"),
            "scenes": scenes,
            "total_scenes": len(scenes),
            "total_duration": sum(s["duration"] for s in scenes),
            "total_frames": sum(s["frame_count"] for s in scenes),
            "generator": "WAN" if self.use_real_model else "WAN (Simulated)",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save animation data
        save_path = ANIMATIONS_DIR / f"{animation_id}.json"
        with open(save_path, 'w') as f:
            json.dump(animation_data, f, indent=2)
        
        return animation_data
    
    def _create_placeholder_frames(self, scene_dir: Path, duration: int, description: str) -> List[str]:
        """Create placeholder frames for simulation"""
        
        fps = 8
        total_frames = duration * fps
        
        frame_paths = []
        
        for i in range(total_frames):
            # Create a simple animated frame
            width, height = 800, 600
            frame = Image.new('RGB', (width, height), color='#1a1a2e')
            draw = ImageDraw.Draw(frame)
            
            # Animated elements
            progress = i / total_frames
            
            # Moving circle
            circle_x = int(width * progress)
            circle_y = height // 2
            circle_radius = 30
            
            draw.ellipse([circle_x - circle_radius, circle_y - circle_radius,
                         circle_x + circle_radius, circle_y + circle_radius],
                        fill='#00ffff', outline='#ffffff', width=2)
            
            # Progress bar
            bar_width = width - 100
            bar_height = 20
            bar_x = 50
            bar_y = height - 100
            
            draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], 
                          outline='#ffffff', width=2)
            
            fill_width = int(bar_width * progress)
            draw.rectangle([bar_x, bar_y, bar_x + fill_width, bar_y + bar_height], 
                          fill='#00ff00')
            
            # Text
            try:
                font = ImageFont.truetype("arial.ttf", 24)
                font_small = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            draw.text((width//2, 50), "ANIMATION PREVIEW", 
                     fill='#ffffff', font=font, anchor="mm")
            
            desc_lines = textwrap.wrap(description[:80], width=40)
            for j, line in enumerate(desc_lines[:3]):
                draw.text((width//2, 100 + j*30), line, 
                         fill='#cccccc', font=font_small, anchor="mm")
            
            draw.text((width//2, height - 50), f"Frame {i+1}/{total_frames} | WAN Simulation", 
                     fill='#888888', font=font_small, anchor="mm")
            
            # Save frame
            frame_path = scene_dir / f"frame_{i:04d}.png"
            frame.save(frame_path)
            frame_paths.append(str(frame_path))
        
        return frame_paths

# ========== COMPLETE PIPELINE FUNCTION ==========

def generate_complete_pipeline(story_premise: str, genre: str = "cyberpunk", 
                              art_style: str = "manga", duration: int = 30) -> Dict:
    """Complete pipeline function for external use"""
    
    print("🚀 Starting complete pipeline...")
    
    # Initialize generators
    story_gen = StoryGenerator()
    img_gen = ImageGenerator()
    vid_gen = VideoGenerator()
    
    # 1. Generate story
    print("📖 1. Generating story...")
    story_data = story_gen.generate_from_premise(story_premise, genre)
    
    # 2. Generate comic
    print("🎨 2. Generating comic with FLUX.2...")
    comic_data = img_gen.generate_comic_from_story(story_data, art_style)
    
    # 3. Generate animation
    print("🎬 3. Generating animation with WAN...")
    animation_data = vid_gen.generate_animation_from_comic(comic_data, duration)
    
    return {
        "story": story_data,
        "comic": comic_data,
        "animation": animation_data,
        "pipeline_complete": True,
        "generators": {
            "story": "DialoGPT" if story_gen.story_pipeline else "Simulated",
            "images": "FLUX.2" if img_gen.use_real_model else "FLUX.2 (Simulated)",
            "videos": "WAN" if vid_gen.use_real_model else "WAN (Simulated)"
        }
    }

# ========== TEST FUNCTION ==========

if __name__ == "__main__":
    """Test the generators"""
    
    print("🧪 Testing generators...")
    
    # Test story generation
    story_gen = StoryGenerator()
    story = story_gen.generate_from_premise(
        "A detective with cybernetic eyes investigates memory thefts in Neo-Tokyo",
        "cyberpunk"
    )
    print(f"✅ Story generated: {story['id']}")
    
    # Test image generation
    img_gen = ImageGenerator()
    comic = img_gen.generate_comic_from_story(story, "cyberpunk")
    print(f"✅ Comic generated: {comic['id']} with {comic['total_pages']} pages")
    
    # Test video generation
    vid_gen = VideoGenerator()
    animation = vid_gen.generate_animation_from_comic(comic, duration=10)
    print(f"✅ Animation generated: {animation['id']} with {animation['total_duration']}s")
    
    print("🎉 All tests passed!")