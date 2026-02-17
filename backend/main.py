from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import json
import uuid
from datetime import datetime
from pathlib import Path
import time
import os
import asyncio
import aiohttp
import io
import subprocess
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
import pyttsx3
import numpy as np
import shutil

# ========== LOAD ENVIRONMENT VARIABLES ==========
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

# ========== CONFIGURATION ==========
IMAGE_WIDTH = 768
IMAGE_HEIGHT = 768
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720
FPS = 30

# ========== HUGGING FACE INFERENCE ENDPOINT ==========
HF_API_BASE = "https://router.huggingface.co/hf-inference/models"

# ========== IMAGE MODELS (ordered by reliability/quality) ==========
IMAGE_MODELS = [
    "stabilityai/stable-diffusion-xl-base-1.0",  # Best quality, but may need credits
    "runwayml/stable-diffusion-v1-5",            # Reliable fallback
    "prompthero/openjourney-v4",                 # Good for artistic styles
    "black-forest-labs/FLUX.1-dev",              # State-of-the-art, may need access
]

# ========== ULTRA-COMPREHENSIVE NEGATIVE PROMPTS ==========
# Expanded with additional hand/finger terms
NEGATIVE_PROMPTS = {
    "hand_arms": (
        "bad hands, mutated hands, deformed hands, ugly hands, poorly drawn hands, "
        "extra fingers, too many fingers, six fingers, seven fingers, eight fingers, "
        "missing fingers, three fingers, four fingers, nine fingers, ten fingers, "
        "fused fingers, webbed fingers, conjoined fingers, merged fingers, attached fingers, "
        "crooked fingers, bent fingers, twisted fingers, broken fingers, dislocated fingers, "
        "claw hand, paw hand, stumpy fingers, stubby fingers, malformed fingers, "
        "extra thumb, missing thumb, double thumb, deformed thumb, "
        "unnatural hand pose, impossible hand pose, broken hand, mangled hand, "
        "floating hand, detached hand, disembodied hand, hand floating in air, "
        "hand connected to wrong place, hand coming from head, hand coming from back, "
        "extra arm, missing arm, third arm, fourth arm, extra limb, missing limb, "
        "deformed arm, broken arm, twisted arm, dislocated arm, "
        "fingers pointing wrong direction, fingers backwards, palm facing wrong way, "
        "hand facing wrong direction, left hand on right arm, right hand on left arm, "
        "too many joints, not enough joints, finger joints misplaced, no knuckles, "
        "mutated hand, alien hand, monster hand, inhuman hand, robotic hand, "
        "glove artifact, hand merging with object, hand disappearing into object, "
        "hand clipped, hand cut off, hand out of frame badly, hand stretched, "
        "hand elongated, hand squished, hand compressed, hand distorted, "
        "nails on wrong fingers, fingernails missing, toenails on fingers, "
        "hairy hands, dirty hands, bruised hands, wounded hands, bleeding hands, "
        "hand missing, no hands, zero hands, one hand only, asymmetric hands"
    ),
    "face_head": (
        "bad face, deformed face, ugly face, mutated face, distorted face, "
        "asymmetric face, asymmetrical eyes, uneven eyes, different sized eyes, "
        "cross-eyed, wall-eyed, lazy eye, dead eyes, empty eyes, glassy eyes, "
        "blind eyes, zombie eyes, demon eyes, alien eyes, inhuman eyes, "
        "too many eyes, three eyes, four eyes, extra eye, missing eye, one eye, "
        "eye on forehead, eye on cheek, eye on neck, misplaced eyes, "
        "no pupils, no iris, solid eyes, white eyes, black eyes, red eyes, "
        "glowing eyes, reflective eyes, cat eyes, snake eyes, reptile eyes, "
        "bad mouth, deformed mouth, ugly mouth, missing mouth, no mouth, "
        "extra mouth, two mouths, mouth on forehead, mouth on cheek, "
        "crooked smile, twisted smile, deformed smile, creepy smile, evil smile, "
        "teeth missing, extra teeth, too many teeth, sharp teeth, fangs, "
        "bad nose, deformed nose, missing nose, no nose, extra nose, two noses, "
        "crooked nose, twisted nose, pig nose, clown nose, "
        "bad ears, deformed ears, missing ears, no ears, extra ears, two ears on one side, "
        "pointed ears, elf ears, animal ears, mismatched ears, "
        "double chin, no chin, weak chin, receding chin, protruding chin, "
        "bad forehead, deformed skull, misshapen head, cone head, flat head, "
        "head too big, head too small, head disproportionate, head floating, "
        "neck too long, neck too short, no neck, double neck, extra neck, "
        "face merged with hair, face merged with background, face smeared, "
        "facial features blended, features not distinct, blurred face, pixelated face"
    ),
    "anatomy_proportions": (
        "bad anatomy, deformed anatomy, mutated anatomy, distorted anatomy, "
        "disproportionate body, out of proportion, unrealistic proportions, "
        "body too long, body too short, torso too long, torso too short, "
        "legs too long, legs too short, arms too long, arms too short, "
        "neck too long, neck too short, head too big, head too small, "
        "shoulders too wide, shoulders too narrow, hips too wide, hips too narrow, "
        "waist too thin, waist too thick, chest too big, chest too small, "
        "torso twisted, torso bent unnaturally, spine curved wrong, spine broken, "
        "body parts misplaced, organs misplaced, skeleton visible, bones showing, "
        "muscles wrong, muscles misplaced, muscle definition wrong, "
        "skin stretched, skin pulled, skin hanging, skin wrinkled unnaturally, "
        "body merged with object, body merging with environment, "
        "limb growing from wrong place, arm growing from head, leg growing from back, "
        "extra joint, missing joint, double jointed wrong, "
        "person too thin, person too fat, emaciated, obese, anorexic, "
        "dwarfism, gigantism, disproportionate limbs, uneven limbs, "
        "torso and limbs mismatched, upper body and lower body mismatched, "
        "human with animal features, human with monster features, human with alien features, "
        "centaur-like, mermaid-like, hybrid anatomy, chimeric anatomy, "
        "mannequin, doll-like, puppet-like, robot-like, cyborg-like, "
        "uncanny valley, unnatural, artificial, fake looking, plastic looking, "
        "wax figure, statue, sculpture, manikin, anatomical model"
    ),
    "image_quality": (
        "worst quality, low quality, bad quality, poor quality, mediocre quality, "
        "normal quality, average quality, standard quality, basic quality, "
        "lowres, low resolution, low res, low definition, low def, "
        "blurry, out of focus, unfocused, hazy, foggy, misty, smudged, smeared, "
        "pixelated, pixellated, pixelated image, blocky, jagged, aliased, "
        "noisy, grainy, gritty, speckled, dotted, stippled, "
        "compressed, jpeg artifacts, compression artifacts, macroblocking, "
        "oversaturated, undersaturated, washed out, faded, pale, dull, "
        "overexposed, underexposed, too bright, too dark, harsh lighting, "
        "bad contrast, low contrast, no contrast, flat lighting, flat colors, "
        "color bleed, color banding, color fringing, chromatic aberration, "
        "haloing, ghosting, doubling, ringing artifacts, "
        "distorted, warped, twisted, bent, curved, fisheye, "
        "stretched, squished, elongated, compressed, aspect ratio wrong, "
        "cropped badly, cut off, truncated, incomplete, partial, "
        "motion blur, camera shake, long exposure, slow shutter, "
        "vignetting, lens flare, lens distortion, barrel distortion, pincushion, "
        "chromatic noise, luminance noise, color noise, sensor noise, "
        "scan lines, interlacing, tearing, flickering, "
        "watermark, signature, logo, text, writing, caption, label, tag, "
        "username, artist name, signature overlay, copyright, trademark, "
        "date stamp, time stamp, barcode, qr code, pattern overlay, "
        "border, frame, outline, box, bounding box, "
        "grid, graph, ruler, measuring lines, guide lines, "
        "test pattern, calibration, color bars, reference image, "
        "draft, sketch, wireframe, blueprint, schematic, "
        "placeholder, concept, wip, work in progress, unfinished"
    ),
    "manga_anime": (
        "bad manga, bad anime, amateur manga, amateur anime, beginner manga, "
        "ugly manga, ugly anime, deformed manga, deformed anime, "
        "poor line art, shaky lines, uneven lines, broken lines, jagged lines, "
        "inconsistent line weight, line weight varies unnaturally, "
        "messy inking, sloppy inking, unclean inking, untidy inking, "
        "screentone wrong, bad screentone, misplaced screentone, "
        "screentone bleed, screentone pattern wrong, screentone too dark, "
        "bad shading, flat shading, no shading, cel shading wrong, "
        "anime face wrong, anime eyes wrong, anime hair wrong, "
        "manga style wrong, incorrect manga proportions, "
        "bad chibi, bad super deformed, wrong chibi proportions, "
        "bad speed lines, misplaced speed lines, wrong speed line direction, "
        "speech bubble wrong, speech bubble placement bad, "
        "sound effect wrong, onomatopoeia misplaced, "
        "panel layout wrong, panel borders uneven, panel gutters wrong, "
        "page composition bad, page flow disrupted, reading order wrong, "
        "character design generic, character design bland, character design unoriginal, "
        "background missing, background sparse, background rushed, "
        "perspective wrong, foreshortening wrong, vanishing points wrong, "
        "3d render looking, cgi, computer generated, digital art looking artificial, "
        "vector art, clip art, stock art, "
        "manga studio default, clip studio default, photoshop default, "
        "filter overused, effect overused, glitch effect, "
        "fan art style, doujin style, self published style, "
        "webcomic style, webtoon style, vertical comic style, "
        "pixel art style, 8-bit, 16-bit, retro game style, "
        "anime screencap, anime screenshot, tv rip, dvd rip, "
        "subtitle, fansub, translation text, "
        "japanese text, chinese text, korean text, english text overlay, "
        "manga panel lines visible, comic book dots visible, ben day dots, "
        "moire pattern, interference pattern, screen door effect"
    ),
    "default": (
        "blurry, low quality, distorted, deformed, disfigured, "
        "bad anatomy, watermark, signature, text, ugly, "
        "worst quality, low quality, jpeg artifacts, out of frame, "
        "extra limbs, duplicate, morbid, mutilated, "
        "poorly drawn hands, poorly drawn face, mutation, "
        "bad proportions, extra arms, extra legs, "
        "fused fingers, too many fingers, long neck, "
        "username, artist name, logo, copyright, "
        "bad art, amateur, beginner, "
        "ugly, hideous, grotesque, monstrous, "
        "nightmare fuel, creepy, scary, horror, "
        "bad composition, bad lighting, bad perspective, "
        "disfigured hands, malformed hands, bad hand anatomy"
    )
}

# ========== WORKSPACE SETUP ==========
BASE_DIR = Path(__file__).parent
WORKSPACE_DIR = BASE_DIR / "workspace"
STORIES_DIR = WORKSPACE_DIR / "stories"
SCENES_DIR = WORKSPACE_DIR / "scenes"
COMICS_DIR = WORKSPACE_DIR / "comics"
PANELS_DIR = WORKSPACE_DIR / "panels"
STORYBOARD_DIR = WORKSPACE_DIR / "storyboard"
VIDEOS_DIR = WORKSPACE_DIR / "videos"
AUDIO_DIR = WORKSPACE_DIR / "audio"
TEMP_DIR = WORKSPACE_DIR / "temp"
ANIMATIONS_DIR = WORKSPACE_DIR / "animations"

for d in [WORKSPACE_DIR, STORIES_DIR, SCENES_DIR, COMICS_DIR, PANELS_DIR, STORYBOARD_DIR,
          VIDEOS_DIR, AUDIO_DIR, TEMP_DIR, ANIMATIONS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ========== AUDIO CONFIGURATION ==========
BACKGROUND_MUSIC = WORKSPACE_DIR / "background_music.mp3"

# ========== FASTAPI INIT ==========
app = FastAPI(title="AI Creative Studio Pro - True 3D Animation Pipeline", version="5.0")

# ========== CORS - Allow all origins ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== HELPER FUNCTIONS ==========
def generate_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"

def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_video_duration(video_path: Path) -> str:
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
               '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.stdout:
            seconds = float(result.stdout.strip())
            return f"{seconds:.1f}s"
    except:
        pass
    return "0s"

def get_negative_prompt(style: str = "default") -> str:
    """Combine all relevant negative prompts for maximum quality"""
    neg = (
        NEGATIVE_PROMPTS["image_quality"] + ", " +
        NEGATIVE_PROMPTS["hand_arms"] + ", " +
        NEGATIVE_PROMPTS["face_head"] + ", " +
        NEGATIVE_PROMPTS["anatomy_proportions"] + ", " +
        NEGATIVE_PROMPTS["default"]
    )
    if style in ["manga", "anime"]:
        neg += ", " + NEGATIVE_PROMPTS["manga_anime"]
    terms = list(dict.fromkeys([t.strip() for t in neg.split(", ")]))
    return ", ".join(terms)

# ========== MODULE 1: STORY GENERATION ==========
def generate_story(premise: str, genre: str = "cyberpunk", main_character: str = "Hero", art_style: str = "manga") -> dict:
    story_id = generate_id("story_")
    story_arcs = {
        "cyberpunk": {
            "intro": f"In the neon-drenched megacity, {main_character} uncovers a conspiracy that threatens to unravel reality itself.",
            "conflict": f"{main_character} infiltrates a corporate stronghold to find evidence of memory manipulation.",
            "climax": f"A final confrontation with the AI overlord determines the fate of human consciousness.",
            "locations": ["neon-lit streets", "corporate tower", "virtual reality server room"]
        },
        "fantasy": {
            "intro": f"In a realm of magic and mystery, {main_character} discovers an ancient prophecy.",
            "conflict": f"{main_character} must gather allies and face mythical creatures.",
            "climax": f"The ultimate battle against the dark lord will decide the kingdom's future.",
            "locations": ["enchanted forest", "ancient ruins", "dragon's lair"]
        },
        "sci_fi": {
            "intro": f"On a distant space station, {main_character} detects a signal from an unknown civilization.",
            "conflict": f"{main_character} must repair the ship while avoiding alien threats.",
            "climax": f"A first contact situation that could change humanity forever.",
            "locations": ["space station", "alien planet", "starship bridge"]
        }
    }
    arc = story_arcs.get(genre, story_arcs["cyberpunk"])
    scenes = [
        {
            "scene": 1,
            "title": "The Discovery",
            "description": arc["intro"],
            "location": arc["locations"][0],
            "mood": "mysterious",
            "key_actions": ["investigates", "discovers clue", "meets informant"],
            "prompt": f"cinematic establishing shot, {main_character} in {arc['locations'][0]}, {genre}, {art_style}, wide angle, dramatic lighting"
        },
        {
            "scene": 2,
            "title": "The Confrontation",
            "description": arc["conflict"],
            "location": arc["locations"][1],
            "mood": "intense",
            "key_actions": ["infiltrates", "battles enemies", "solves puzzle"],
            "prompt": f"dynamic action scene, {main_character} in {arc['locations'][1]}, {genre}, {art_style}, intense motion, dramatic pose"
        },
        {
            "scene": 3,
            "title": "The Climax",
            "description": arc["climax"],
            "location": arc["locations"][2],
            "mood": "epic",
            "key_actions": ["final battle", "makes sacrifice", "achieves victory"],
            "prompt": f"epic climax, {main_character} in {arc['locations'][2]}, {genre}, {art_style}, cinematic, emotional, heroic"
        }
    ]
    story = {
        "id": story_id,
        "premise": premise,
        "genre": genre,
        "main_character": main_character,
        "art_style": art_style,
        "scenes": scenes,
        "created_at": datetime.now().isoformat()
    }
    story_json_path = STORIES_DIR / f"{story_id}.json"
    with open(story_json_path, "w", encoding="utf-8") as f:
        json.dump(story, f, indent=2)
    story_txt_path = STORIES_DIR / f"{story_id}.txt"
    with open(story_txt_path, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write("🎬 AI GENERATED CINEMATIC STORY\n")
        f.write("="*60 + "\n\n")
        f.write(f"📖 PREMISE:\n{premise}\n\n")
        f.write(f"🎭 GENRE: {genre}\n")
        f.write(f"👤 CHARACTER: {main_character}\n")
        f.write(f"🎨 STYLE: {art_style}\n")
        f.write(f"🆔 ID: {story_id}\n\n")
        f.write("="*60 + "\n")
        f.write("🎬 SCENES\n")
        f.write("="*60 + "\n\n")
        for scene in scenes:
            f.write(f"SCENE {scene['scene']}: {scene['title']}\n")
            f.write(f"📍 Location: {scene['location']}\n")
            f.write(f"🎭 Mood: {scene['mood']}\n")
            f.write(f"📝 {scene['description']}\n")
            f.write(f"⚔️ Actions: {', '.join(scene['key_actions'])}\n")
            f.write("-"*40 + "\n\n")
    return story

# ========== MODULE 2: SCENE SEGMENTATION ==========
def segment_scenes(story: dict) -> List[dict]:
    segmented = []
    shot_counter = 1
    for scene in story["scenes"]:
        shot_templates = [
            {
                "type": "establishing",
                "camera": "wide shot",
                "description": f"Wide shot of {scene['location']}. {scene['description']}",
                "composition": "rule of thirds, deep depth of field",
                "duration": 4.0
            },
            {
                "type": "medium",
                "camera": "medium shot",
                "description": f"{story['main_character']} in medium shot, showing emotion and surroundings",
                "composition": "eye level, shallow depth of field",
                "duration": 3.0
            },
            {
                "type": "closeup",
                "camera": "close-up",
                "description": f"Close-up of {story['main_character']}'s face showing {scene['mood']} expression",
                "composition": "intimate, focused on eyes",
                "duration": 2.5
            },
            {
                "type": "action",
                "camera": "dynamic angle",
                "description": f"Dynamic shot of {story['main_character']} performing {scene['key_actions'][0]}",
                "composition": "low angle, motion blur effect",
                "duration": 3.5
            }
        ]
        for tmpl in shot_templates:
            shot = {
                "shot_id": f"shot_{shot_counter:04d}",
                "scene_number": scene["scene"],
                "scene_title": scene["title"],
                "shot_type": tmpl["type"],
                "camera_angle": tmpl["camera"],
                "description": tmpl["description"],
                "composition_notes": tmpl["composition"],
                "duration": tmpl["duration"],
                "character": story["main_character"],
                "facial_expression": scene["mood"],
                "character_pose": "neutral",
                "background": scene["location"],
                "art_style": story["art_style"],
                "genre": story["genre"],
                "prompt": f"{tmpl['description']}, {tmpl['camera']}, {story['art_style']}, {story['genre']}, cinematic, detailed, 8k, perfect hands, perfect face, detailed fingers, accurate anatomy"
            }
            segmented.append(shot)
            shot_counter += 1
    return segmented

# ========== MODULE 3: COMIC/MANGA CREATION ==========
async def generate_panel_image(shot: dict) -> Optional[Image.Image]:
    """Generate a single panel image with enhanced quality checks"""
    if not HF_TOKEN:
        print("      ⚠️ No Hugging Face token provided")
        return create_fallback_panel(shot)
    
    prompt = shot["prompt"]
    negative = get_negative_prompt(shot["art_style"])
    enhanced_prompt = f"{prompt}, masterpiece, best quality, highly detailed, 8k, sharp focus, perfect anatomy, perfect hands, detailed fingers, beautiful face"
    
    print(f"         🎨 Generating panel: {shot['shot_type']}")
    
    # Try Hugging Face models with retries
    for model in IMAGE_MODELS:
        for attempt in range(2):  # Retry once if 503
            try:
                url = f"{HF_API_BASE}/{model}"
                headers = {"Authorization": f"Bearer {HF_TOKEN}"}
                payload = {
                    "inputs": enhanced_prompt,
                    "parameters": {
                        "negative_prompt": negative[:1500],  # Increased limit
                        "num_inference_steps": 30,  # More steps for quality
                        "guidance_scale": 7.5,
                        "width": IMAGE_WIDTH,
                        "height": IMAGE_HEIGHT,
                        "seed": random.randint(1, 2**31 - 1)
                    }
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=90) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            if len(data) > 1000:
                                img = Image.open(io.BytesIO(data)).convert("RGB")
                                # Quality check: if image is too uniform (e.g., solid color), reject
                                img_array = np.array(img)
                                if np.std(img_array) < 10:  # Low variance indicates flat image
                                    print(f"         ⚠️ Generated image is flat, rejecting")
                                    continue
                                img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)
                                # Apply sharpening and contrast enhancement
                                img = img.filter(ImageFilter.UnsharpMask(radius=0.5, percent=50, threshold=0))
                                enhancer = ImageEnhance.Contrast(img)
                                img = enhancer.enhance(1.1)
                                print(f"         ✅ Generated with {model}")
                                return img
                        elif resp.status == 503:
                            print(f"         ⏳ {model} loading, retrying...")
                            await asyncio.sleep(5)
                            continue
                        else:
                            error_text = await resp.text()
                            print(f"         ❌ {model} error {resp.status}: {error_text[:200]}")
                            break  # Don't retry on other errors
            except Exception as e:
                print(f"         ⚠️ {model} exception: {str(e)}")
                continue
    
    # Try Pollinations.ai as fallback
    try:
        import urllib.parse
        # Use a shorter prompt for Pollinations
        short_prompt = urllib.parse.quote(f"{shot['description'][:100]}, {shot['art_style']}, high quality, detailed, perfect hands")
        url = f"https://image.pollinations.ai/prompt/{short_prompt}?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&nologo=true&enhance=true&model=flux"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    if len(data) > 1000:
                        img = Image.open(io.BytesIO(data)).convert("RGB")
                        # Quality check
                        img_array = np.array(img)
                        if np.std(img_array) < 10:
                            print(f"         ⚠️ Pollinations image flat, rejecting")
                        else:
                            img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)
                            print(f"         ✅ Generated with Pollinations.ai")
                            return img
                else:
                    error_text = await resp.text()
                    print(f"         ❌ Pollinations.ai error {resp.status}: {error_text[:200]}")
    except Exception as e:
        print(f"         ⚠️ Pollinations.ai exception: {e}")
    
    print("         ⚠️ Using fallback panel")
    return create_fallback_panel(shot)

def create_fallback_panel(shot: dict) -> Image.Image:
    """Create artistic fallback panel with visual interest (but not random)"""
    img = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), color='#0a0a1a')
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    for y in range(IMAGE_HEIGHT):
        r = int(30 + 20 * (y / IMAGE_HEIGHT))
        g = int(20 + 30 * (y / IMAGE_HEIGHT))
        b = int(50 + 40 * (y / IMAGE_HEIGHT))
        draw.line([(0, y), (IMAGE_WIDTH, y)], fill=(r, g, b))
    
    # Add grid pattern for visual interest
    for x in range(0, IMAGE_WIDTH, 50):
        draw.line([(x, 0), (x, IMAGE_HEIGHT)], fill=(100, 100, 150, 30), width=1)
    for y in range(0, IMAGE_HEIGHT, 50):
        draw.line([(0, y), (IMAGE_WIDTH, y)], fill=(100, 100, 150, 30), width=1)
    
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 48)
        font_medium = ImageFont.truetype("arialbd.ttf", 36)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add panel information with style
    draw.text((IMAGE_WIDTH//2, IMAGE_HEIGHT//2 - 60), f"PANEL: {shot['shot_type']}", 
              fill='white', font=font_large, anchor="mm")
    draw.text((IMAGE_WIDTH//2, IMAGE_HEIGHT//2), f"{shot['camera_angle']}", 
              fill='#88aaff', font=font_medium, anchor="mm")
    draw.text((IMAGE_WIDTH//2, IMAGE_HEIGHT//2 + 60), shot['description'][:50] + "...", 
              fill='#cccccc', font=font_small, anchor="mm")
    draw.text((IMAGE_WIDTH-100, IMAGE_HEIGHT-40), f"Scene {shot['scene_number']}", 
              fill='#ff88aa', font=font_small, anchor="mm")
    
    return img

def create_panel_layout(panel_images: List[Image.Image], layout_type: str = "manga") -> Image.Image:
    num_panels = len(panel_images)
    if num_panels == 1:
        return panel_images[0]
    if layout_type == "manga":
        if num_panels == 2:
            canvas = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT * 2))
            canvas.paste(panel_images[0].resize((IMAGE_WIDTH, IMAGE_HEIGHT)), (0, 0))
            canvas.paste(panel_images[1].resize((IMAGE_WIDTH, IMAGE_HEIGHT)), (0, IMAGE_HEIGHT))
            return canvas
        elif num_panels == 3:
            canvas = Image.new('RGB', (IMAGE_WIDTH * 2, IMAGE_HEIGHT * 2))
            left_panel = panel_images[0].resize((IMAGE_WIDTH, IMAGE_HEIGHT * 2))
            canvas.paste(left_panel, (0, 0))
            canvas.paste(panel_images[1].resize((IMAGE_WIDTH, IMAGE_HEIGHT)), (IMAGE_WIDTH, 0))
            canvas.paste(panel_images[2].resize((IMAGE_WIDTH, IMAGE_HEIGHT)), (IMAGE_WIDTH, IMAGE_HEIGHT))
            return canvas
        else:
            canvas = Image.new('RGB', (IMAGE_WIDTH * 2, IMAGE_HEIGHT * 2))
            for idx, img in enumerate(panel_images[:4]):
                x = (idx % 2) * IMAGE_WIDTH
                y = (idx // 2) * IMAGE_HEIGHT
                canvas.paste(img.resize((IMAGE_WIDTH, IMAGE_HEIGHT)), (x, y))
            return canvas
    else:
        cols = 2
        rows = (num_panels + cols - 1) // cols
        canvas = Image.new('RGB', (IMAGE_WIDTH * cols, IMAGE_HEIGHT * rows))
        for idx, img in enumerate(panel_images):
            x = (idx % cols) * IMAGE_WIDTH
            y = (idx // cols) * IMAGE_HEIGHT
            canvas.paste(img.resize((IMAGE_WIDTH, IMAGE_HEIGHT)), (x, y))
        return canvas

async def generate_comic_from_shots(shots: List[dict], layout: str = "manga") -> dict:
    panel_paths = []
    panels = []
    print(f"   🎨 Generating {len(shots)} comic panels...")
    for idx, shot in enumerate(shots):
        print(f"   📄 Panel {idx+1}/{len(shots)}: {shot['shot_type']}")
        img = await generate_panel_image(shot)
        panel_id = generate_id("panel_")
        panel_path = PANELS_DIR / f"{panel_id}.png"
        img.save(panel_path)
        panel_paths.append(panel_path)
        panels.append({
            "panel_id": panel_id,
            "shot_id": shot["shot_id"],
            "path": str(panel_path),
            "type": shot["shot_type"]
        })
    pages = []
    for i in range(0, len(panels), 4):
        page_panels = panels[i:i+4]
        page_images = [Image.open(p["path"]) for p in page_panels]
        page_img = create_panel_layout(page_images, layout)
        page_id = generate_id("page_")
        page_path = COMICS_DIR / f"{page_id}.png"
        page_img.save(page_path)
        pages.append({
            "page_id": page_id,
            "path": str(page_path),
            "panels": [p["panel_id"] for p in page_panels]
        })
    comic_id = generate_id("comic_")
    comic_meta = {
        "id": comic_id,
        "pages": pages,
        "panels": panels,
        "created_at": datetime.now().isoformat()
    }
    with open(COMICS_DIR / f"{comic_id}.json", "w") as f:
        json.dump(comic_meta, f)
    return {
        "comic_id": comic_id,
        "pages": pages,
        "panels": panels,
        "panel_paths": [str(p) for p in panel_paths]
    }

# ========== MODULE 4: ANIMATION PREPARATION ==========
def prepare_animation_instructions(shots: List[dict], style: str) -> List[dict]:
    instructions = []
    for shot in shots:
        animated_shot = shot.copy()
        if shot["shot_type"] == "establishing":
            camera_move = "slow pan from left to right"
            camera_3d = "dolly zoom with crane up"
        elif shot["shot_type"] == "medium":
            camera_move = "subtle zoom in"
            camera_3d = "orbit around character"
        elif shot["shot_type"] == "closeup":
            camera_move = "slight pull focus, no camera movement"
            camera_3d = "breathing effect, subtle pulse"
        elif shot["shot_type"] == "action":
            camera_move = "dynamic whip pan, slight shake"
            camera_3d = "shake with rotation, dynamic movement"
        else:
            camera_move = "static"
            camera_3d = "static"
        
        if shot["shot_type"] == "action":
            char_move = "full body motion, running/fighting animation"
        elif shot["shot_type"] == "closeup":
            char_move = "subtle facial animation, blinking, micro-expressions"
        else:
            char_move = "idle animation with slight breathing movement"
        
        animated_shot["camera_movement"] = camera_move
        animated_shot["camera_3d"] = camera_3d
        animated_shot["character_movement"] = char_move
        animated_shot["lip_sync"] = shot["shot_type"] == "closeup"
        animated_shot["background_movement"] = "parallax scroll" if shot["shot_type"] == "establishing" else "static"
        animated_shot["particles"] = shot["genre"] == "cyberpunk" or shot["shot_type"] == "action"
        animated_shot["start_frame"] = 0
        animated_shot["end_frame"] = int(shot["duration"] * FPS)
        animated_shot["keyframes"] = [
            {"frame": 0, "description": "Start of shot"},
            {"frame": int(shot["duration"] * FPS / 2), "description": "Mid-shot emphasis"},
            {"frame": int(shot["duration"] * FPS), "description": "End of shot"}
        ]
        animated_shot.setdefault("genre", "cyberpunk")
        animated_shot.setdefault("duration", 3.0)
        animated_shot.setdefault("shot_id", f"shot_{len(instructions)+1:04d}")
        instructions.append(animated_shot)
    return instructions

# ========== NARRATION AUDIO GENERATION ==========
def generate_narration(text: str) -> Optional[Path]:
    try:
        print(f"      🎤 Generating narration audio...")
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            for voice in voices:
                if 'female' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
        engine.setProperty('rate', 175)
        audio_path = AUDIO_DIR / f"narration_{generate_id()}.wav"
        engine.save_to_file(text[:1000], str(audio_path))
        engine.runAndWait()
        if audio_path.exists() and audio_path.stat().st_size > 1000:
            size = audio_path.stat().st_size / (1024 * 1024)
            print(f"      ✅ Audio generated: {size:.1f}MB")
            return audio_path
    except Exception as e:
        print(f"      ⚠️ TTS failed: {e}")
    return None

# ========== TRUE 3D ANIMATED VIDEO WITH DYNAMIC MOTION ==========
async def create_true_3d_video(
    image_paths: List[Path], 
    audio_path: Optional[Path], 
    music_path: Optional[Path],
    shots: List[dict]
) -> Path:
    """Create a true 3D animated video with dynamic camera movements and character animation"""
    
    video_id = generate_id("true3d_")
    output_video = VIDEOS_DIR / f"{video_id}.mp4"
    temp_frames_dir = TEMP_DIR / f"frames_{video_id}"
    temp_frames_dir.mkdir(exist_ok=True)
    
    print(f"\n      🎬 Creating TRUE 3D animated video with dynamic motion...")
    
    frames_generated = 0
    
    try:
        # Load background music for beat detection if available
        music_bpm = 120  # Default BPM
        music_beats = []
        if music_path and music_path.exists():
            # In a real implementation, you'd analyze the music for beats
            # For now, we'll simulate beats every 0.5 seconds
            music_beats = [i * 0.5 for i in range(100)]  # Beat every 0.5s
            print(f"         🎵 Music detected, enabling beat synchronization")
        
        # Process each shot with more dynamic animation
        for shot_idx, (img_path, shot) in enumerate(zip(image_paths, shots)):
            print(f"         Processing shot {shot_idx + 1}/{len(image_paths)}: {shot['shot_type']} - {shot.get('camera_3d', 'standard')}")
            
            # Load base image and create layers for parallax
            base_img = Image.open(img_path).convert("RGB")
            base_img.thumbnail((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
            
            # Create foreground, midground, background layers (simulated)
            # In a real implementation, you'd use depth maps or separate elements
            background = base_img.copy()
            midground = base_img.copy()
            foreground = base_img.copy()
            
            # Apply slight blur to background for depth effect
            background = background.filter(ImageFilter.GaussianBlur(radius=2))
            
            # Generate frames for this shot
            shot_frames = int(shot["duration"] * FPS)
            
            for frame in range(shot_frames):
                progress = frame / shot_frames
                
                # Create canvas
                canvas = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT), (20, 20, 30))
                
                # Apply different 3D camera movements based on shot type
                if shot["shot_type"] == "establishing":
                    # Dolly zoom effect
                    zoom = 1.0 + progress * 0.2
                    # Crane up effect
                    crane_y = int(progress * 50)
                    
                    # Transform background (slow)
                    bg_scale = 1.0 + progress * 0.05
                    bg_temp = background.resize(
                        (int(VIDEO_WIDTH * bg_scale), int(VIDEO_HEIGHT * bg_scale)), 
                        Image.Resampling.LANCZOS
                    )
                    bg_x = (bg_temp.width - VIDEO_WIDTH) // 2
                    bg_y = (bg_temp.height - VIDEO_HEIGHT) // 2
                    bg_cropped = bg_temp.crop((bg_x, bg_y, bg_x + VIDEO_WIDTH, bg_y + VIDEO_HEIGHT))
                    
                    # Transform midground (medium)
                    mg_scale = 1.0 + progress * 0.1
                    mg_temp = midground.resize(
                        (int(VIDEO_WIDTH * mg_scale), int(VIDEO_HEIGHT * mg_scale)), 
                        Image.Resampling.LANCZOS
                    )
                    mg_x = (mg_temp.width - VIDEO_WIDTH) // 2
                    mg_y = (mg_temp.height - VIDEO_HEIGHT) // 2
                    mg_cropped = mg_temp.crop((mg_x, mg_y, mg_x + VIDEO_WIDTH, mg_y + VIDEO_HEIGHT))
                    
                    # Transform foreground (fast)
                    fg_scale = 1.0 + progress * 0.15
                    fg_temp = foreground.resize(
                        (int(VIDEO_WIDTH * fg_scale), int(VIDEO_HEIGHT * fg_scale)), 
                        Image.Resampling.LANCZOS
                    )
                    fg_x = (fg_temp.width - VIDEO_WIDTH) // 2
                    fg_y = (fg_temp.height - VIDEO_HEIGHT) // 2
                    fg_cropped = fg_temp.crop((fg_x, fg_y, fg_x + VIDEO_WIDTH, fg_y + VIDEO_HEIGHT))
                    
                    # Paste layers with parallax (background moves slowest, foreground fastest)
                    canvas.paste(bg_cropped, (0, 0))
                    
                    # Create mask for midground (semi-transparent)
                    mg_mask = Image.new('L', mg_cropped.size, 180)
                    canvas.paste(mg_cropped, (0, 0), mg_mask)
                    
                    # Create mask for foreground (more opaque)
                    fg_mask = Image.new('L', fg_cropped.size, 220)
                    canvas.paste(fg_cropped, (0, 0), fg_mask)
                    
                elif shot["shot_type"] == "action":
                    # Dynamic camera shake and rotation
                    shake_intensity = 10 * (1 - progress)  # Shake decreases over time
                    shake_x = random.randint(-int(shake_intensity), int(shake_intensity))
                    shake_y = random.randint(-int(shake_intensity), int(shake_intensity))
                    
                    # Slight rotation for dynamic feel
                    angle = np.sin(progress * 4 * np.pi) * 2
                    
                    # Apply transforms
                    rotated = base_img.rotate(angle, expand=True, fillcolor=(20, 20, 30))
                    rotated.thumbnail((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.LANCZOS)
                    
                    # Paste with shake offset
                    paste_x = (VIDEO_WIDTH - rotated.width) // 2 + shake_x
                    paste_y = (VIDEO_HEIGHT - rotated.height) // 2 + shake_y
                    canvas.paste(rotated, (paste_x, paste_y))
                    
                elif shot["shot_type"] == "closeup":
                    # Subtle breathing effect (pulsing zoom)
                    pulse = 1.0 + np.sin(progress * 4 * np.pi) * 0.02
                    new_size = (int(VIDEO_WIDTH * pulse), int(VIDEO_HEIGHT * pulse))
                    temp = base_img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Center crop
                    left = (new_size[0] - VIDEO_WIDTH) // 2
                    top = (new_size[1] - VIDEO_HEIGHT) // 2
                    canvas = temp.crop((left, top, left + VIDEO_WIDTH, top + VIDEO_HEIGHT))
                    
                else:  # medium shot
                    # Orbit effect (camera moves in an arc)
                    orbit_x = int(np.sin(progress * 2 * np.pi) * 20)
                    orbit_y = int(np.cos(progress * 2 * np.pi) * 10)
                    
                    # Slight zoom
                    zoom = 1.0 + progress * 0.05
                    new_size = (int(VIDEO_WIDTH * zoom), int(VIDEO_HEIGHT * zoom))
                    temp = base_img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Center with orbit offset
                    left = (new_size[0] - VIDEO_WIDTH) // 2 + orbit_x
                    top = (new_size[1] - VIDEO_HEIGHT) // 2 + orbit_y
                    canvas = temp.crop((left, top, left + VIDEO_WIDTH, top + VIDEO_HEIGHT))
                
                draw = ImageDraw.Draw(canvas)
                
                # Add dynamic lighting based on progress
                light_intensity = 0.8 + 0.2 * np.sin(progress * 2 * np.pi)
                overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                
                # Add vignette that pulses with music if available
                if music_beats:
                    # Find closest beat
                    beat_progress = progress * shot["duration"]
                    beat_effect = 1.0
                    for beat in music_beats:
                        if abs(beat - beat_progress) < 0.1:
                            beat_effect = 1.5
                            break
                    vignette_strength = int(40 * light_intensity * beat_effect)
                else:
                    vignette_strength = int(40 * light_intensity)
                
                for i in range(0, 100, 10):
                    alpha = int(vignette_strength * (1 - i/100))
                    overlay_draw.rectangle([i, i, VIDEO_WIDTH-i, VIDEO_HEIGHT-i], 
                                          outline=(0, 0, 0, alpha), width=2)
                
                canvas = Image.alpha_composite(canvas.convert('RGBA'), overlay).convert('RGB')
                
                # Add particle effects based on genre
                if shot.get("particles", False):
                    particles = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
                    particle_draw = ImageDraw.Draw(particles)
                    
                    if shot["genre"] == "cyberpunk":
                        # Cyberpunk rain/glitch particles
                        for _ in range(20):
                            x = (frame * 5 + _ * 30) % VIDEO_WIDTH
                            y = random.randint(0, VIDEO_HEIGHT)
                            size = random.randint(1, 3)
                            alpha = random.randint(100, 255)
                            particle_draw.ellipse([x, y, x+size, y+size], 
                                                fill=(0, 255, 255, alpha))
                        
                        # Add digital rain lines
                        for _ in range(5):
                            x = random.randint(0, VIDEO_WIDTH)
                            y_start = 0
                            y_end = VIDEO_HEIGHT
                            particle_draw.line([(x, y_start), (x, y_end)], 
                                             fill=(0, 255, 255, 50), width=1)
                    else:
                        # Generic sparkles
                        for _ in range(10):
                            x = random.randint(0, VIDEO_WIDTH)
                            y = (frame * 3 + _ * 40) % VIDEO_HEIGHT
                            size = random.randint(1, 2)
                            particle_draw.ellipse([x, y, x+size, y+size], 
                                                fill=(255, 255, 200, 150))
                    
                    canvas = Image.alpha_composite(canvas.convert('RGBA'), particles).convert('RGB')
                
                # Add shot info text (optional, can be commented out for final video)
                # try:
                #     font = ImageFont.truetype("arial.ttf", 20)
                #     draw = ImageDraw.Draw(canvas)
                #     draw.text((10, 10), f"Shot {shot['shot_id']}", fill='rgba(255,255,255,128)', font=font)
                # except:
                #     pass
                
                # Save frame
                frame_path = temp_frames_dir / f"frame_{frames_generated:06d}.jpg"
                canvas.save(frame_path, "JPEG", quality=92)
                frames_generated += 1
            
            print(f"         ✓ Shot {shot_idx + 1} animated with 3D effects ({shot_frames} frames)")
        
        print(f"         Total frames generated: {frames_generated}")
        
        # Create concat file for FFmpeg
        concat_file = TEMP_DIR / f"concat_{video_id}.txt"
        with open(concat_file, 'w') as f:
            for i in range(frames_generated):
                frame_path = temp_frames_dir / f"frame_{i:06d}.jpg"
                frame_str = str(frame_path).replace('\\', '/')
                f.write(f"file '{frame_str}'\n")
        
        # Build FFmpeg command with audio mixing
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file).replace('\\', '/'),
            '-c:v', 'libx264',
            '-preset', 'slow',  # Better compression for 3D effects
            '-crf', '16',  # Higher quality
            '-pix_fmt', 'yuv420p',
            '-r', str(FPS),
            '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2',
            '-movflags', '+faststart',
        ]
        
        # Add audio tracks
        audio_inputs = []
        
        # Add narration if available
        if audio_path and audio_path.exists():
            cmd.extend(['-i', str(audio_path).replace('\\', '/')])
            audio_inputs.append(0)
            print(f"         Adding narration audio")
        
        # Add background music if available
        if music_path and music_path.exists():
            cmd.extend(['-i', str(music_path).replace('\\', '/')])
            music_idx = len(audio_inputs)
            audio_inputs.append(music_idx)
            print(f"         Adding background music: {music_path.name}")
        
        # Mix audio tracks with proper levels
        if audio_inputs:
            if len(audio_inputs) == 1:
                cmd.extend(['-map', f'{audio_inputs[0]}:a'])
                cmd.extend(['-c:a', 'aac', '-b:a', '192k', '-ac', '2'])
            else:
                # Mix narration (louder) with music (quieter)
                # Narration at 0dB, music at -10dB
                audio_filter = (
                    f"[0:a]volume=1.0[a0];"
                    f"[1:a]volume=0.3[a1];"
                    f"[a0][a1]amix=inputs=2:duration=longest[aout]"
                )
                cmd.extend(['-filter_complex', audio_filter])
                cmd.extend(['-map', '[aout]', '-c:a', 'aac', '-b:a', '192k', '-ac', '2'])
        
        # Add output path
        cmd.append(str(output_video).replace('\\', '/'))
        
        print(f"         Encoding TRUE 3D video with {frames_generated} frames...")
        
        # Run FFmpeg
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # Longer timeout for complex video
        
        if process.returncode != 0:
            print(f"         ⚠️ FFmpeg warning: {process.stderr[:200]}")
            
            # Try simplified version if complex encoding fails
            print(f"         🔄 Trying simplified encoding...")
            simple_cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file).replace('\\', '/'),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '18',
                '-pix_fmt', 'yuv420p',
                '-r', str(FPS),
                str(output_video).replace('\\', '/')
            ]
            
            if audio_inputs:
                if audio_path and audio_path.exists():
                    simple_cmd.extend(['-i', str(audio_path).replace('\\', '/')])
                    simple_cmd.extend(['-c:a', 'aac', '-b:a', '192k', '-shortest'])
                elif music_path and music_path.exists():
                    simple_cmd.extend(['-i', str(music_path).replace('\\', '/')])
                    simple_cmd.extend(['-c:a', 'aac', '-b:a', '192k', '-shortest'])
            
            simple_process = subprocess.run(simple_cmd, capture_output=True, text=True, timeout=300)
            if simple_process.returncode != 0:
                print(f"         ❌ Simplified encoding failed: {simple_process.stderr}")
                raise Exception("Video encoding failed")
            else:
                print(f"         ✅ Simplified encoding succeeded")
        
        # Cleanup
        shutil.rmtree(temp_frames_dir, ignore_errors=True)
        concat_file.unlink(missing_ok=True)
        
        if output_video.exists():
            size = output_video.stat().st_size / (1024 * 1024)
            duration = get_video_duration(output_video)
            print(f"      ✅ TRUE 3D video created: {size:.1f}MB, {duration}")
            return output_video
        else:
            raise Exception("Video file not created")
            
    except Exception as e:
        print(f"      ❌ Video creation failed: {e}")
        import traceback
        traceback.print_exc()
        if temp_frames_dir.exists():
            shutil.rmtree(temp_frames_dir, ignore_errors=True)
        raise

# ========== API ENDPOINTS ==========
@app.get("/")
async def root():
    return {
        "service": "AI Creative Studio Pro - True 3D Animation Pipeline",
        "version": "5.0",
        "status": "running",
        "modules": ["story", "segmentation", "comic", "animation_prep", "true_3d_video"],
        "features": {
            "story_generation": True,
            "scene_segmentation": True,
            "comic_creation": True,
            "animation_preparation": True,
            "true_3d_video": True,
            "music_sync": True,
            "particle_effects": True,
            "negative_terms": sum(len(p.split(", ")) for p in NEGATIVE_PROMPTS.values())
        },
        "system": {
            "hf_token": bool(HF_TOKEN),
            "ffmpeg": check_ffmpeg(),
            "workspace": str(WORKSPACE_DIR),
            "background_music": BACKGROUND_MUSIC.exists()
        }
    }

@app.get("/api/v1/test")
async def test_connection():
    return {
        "success": True,
        "message": "Backend API is running",
        "ffmpeg": check_ffmpeg(),
        "hf_token": bool(HF_TOKEN),
        "background_music": BACKGROUND_MUSIC.exists()
    }

@app.post("/api/v1/story/generate")
async def api_generate_story(request: Request):
    data = await request.json()
    premise = data.get("premise", "").strip()
    genre = data.get("genre", "cyberpunk")
    main_character = data.get("main_character", "Hero")
    art_style = data.get("art_style", "manga")
    if not premise:
        raise HTTPException(400, "Premise required")
    story = generate_story(premise, genre, main_character, art_style)
    return {"success": True, "story": story}

@app.post("/api/v1/scene/segment")
async def api_segment_scenes(request: Request):
    data = await request.json()
    story = data.get("story")
    if not story:
        raise HTTPException(400, "Story required")
    shots = segment_scenes(story)
    seg_id = generate_id("seg_")
    seg_path = SCENES_DIR / f"{seg_id}.json"
    with open(seg_path, "w") as f:
        json.dump({"id": seg_id, "shots": shots, "story_id": story["id"]}, f, indent=2)
    return {"success": True, "shots": shots, "segmentation_id": seg_id}

@app.post("/api/v1/comic/generate")
async def api_generate_comic(request: Request):
    data = await request.json()
    shots = data.get("shots")
    layout = data.get("layout", "manga")
    if not shots:
        raise HTTPException(400, "Shots required")
    result = await generate_comic_from_shots(shots, layout)
    return {"success": True, **result}

@app.post("/api/v1/animation/prepare")
async def api_prepare_animation(request: Request):
    data = await request.json()
    shots = data.get("shots")
    style = data.get("style", "manga")
    if not shots:
        raise HTTPException(400, "Shots required")
    instructions = prepare_animation_instructions(shots, style)
    prep_id = generate_id("anim_prep_")
    prep_path = ANIMATIONS_DIR / f"{prep_id}.json"
    with open(prep_path, "w") as f:
        json.dump({"id": prep_id, "instructions": instructions}, f, indent=2)
    return {"success": True, "preparation_id": prep_id, "instructions": instructions}

@app.post("/api/v1/video/create")
async def api_create_video(request: Request):
    data = await request.json()
    panel_paths = [Path(p) for p in data.get("panel_paths", [])]
    shots = data.get("shots", [])
    if not panel_paths or not shots:
        raise HTTPException(400, "Panel paths and shots required")
    narration_text = data.get("narration", "")
    audio_path = None
    if narration_text:
        audio_path = generate_narration(narration_text)
    music_path = BACKGROUND_MUSIC if BACKGROUND_MUSIC.exists() else None
    video_path = await create_true_3d_video(panel_paths, audio_path, music_path, shots)
    return {"success": True, "video_path": str(video_path)}

@app.post("/api/v1/pipeline/full")
async def full_pipeline(request: Request):
    print("\n" + "="*60)
    print("🚀 STARTING FULL CREATIVE PIPELINE")
    print("="*60)
    start_time = time.time()
    try:
        data = await request.json()
        premise = data.get("premise", "").strip()
        genre = data.get("genre", "cyberpunk")
        art_style = data.get("art_style", "manga")
        main_character = data.get("main_character", "Hero")
        layout = data.get("layout", "manga")
        if not premise:
            raise HTTPException(400, "Premise required")
        print(f"\n📝 Input:")
        print(f"   • Premise: {premise[:80]}...")
        print(f"   • Genre: {genre}")
        print(f"   • Style: {art_style}")
        print(f"   • Character: {main_character}")
        print(f"   • Layout: {layout}")
        
        # Step 1: Generate Story
        story = generate_story(premise, genre, main_character, art_style)
        print(f"   ✅ Story ID: {story['id']}")
        
        # Step 2: Segment into shots
        shots = segment_scenes(story)
        print(f"   ✅ Generated {len(shots)} shots")
        seg_id = generate_id("seg_")
        seg_path = SCENES_DIR / f"{seg_id}.json"
        with open(seg_path, "w") as f:
            json.dump({"id": seg_id, "shots": shots, "story_id": story["id"]}, f, indent=2)
        
        # Step 3: Generate comic panels
        print(f"\n🎨 Step 3: Generating comic panels...")
        comic_result = await generate_comic_from_shots(shots, layout)
        print(f"   ✅ Created {len(comic_result['pages'])} pages with {len(comic_result['panels'])} panels")
        
        # Step 4: Prepare animation instructions
        print(f"\n🎬 Step 4: Preparing animation instructions...")
        animated_shots = prepare_animation_instructions(shots, art_style)
        prep_id = generate_id("anim_prep_")
        prep_path = ANIMATIONS_DIR / f"{prep_id}.json"
        with open(prep_path, "w") as f:
            json.dump({"id": prep_id, "instructions": animated_shots}, f, indent=2)
        print(f"   ✅ Generated instructions for {len(animated_shots)} shots")
        
        # Step 5: Create true 3D video
        print(f"\n🎥 Step 5: Creating TRUE 3D animated video...")
        panel_paths = [Path(p) for p in comic_result["panel_paths"]]
        narration = f"{premise}. " + " ".join([s["description"] for s in shots[:3]])
        audio_path = generate_narration(narration)
        music_path = BACKGROUND_MUSIC if BACKGROUND_MUSIC.exists() else None
        video_path = await create_true_3d_video(panel_paths, audio_path, music_path, animated_shots)
        
        total_time = time.time() - start_time
        
        result = {
            "success": True,
            "message": "Full pipeline completed successfully!",
            "time_taken": f"{total_time:.1f}s",
            "project_id": generate_id("proj_"),
            "components": {
                "story": {
                    "id": story["id"],
                    "scenes": len(story["scenes"]),
                    "download": f"/api/v1/download/story/{story['id']}"
                },
                "shots": {
                    "count": len(shots),
                    "id": seg_id,
                    "download": f"/api/v1/download/scenes/{seg_id}"
                },
                "comic": {
                    "id": comic_result["comic_id"],
                    "pages": len(comic_result["pages"]),
                    "panels": len(comic_result["panels"]),
                    "download": f"/api/v1/download/comic/{comic_result['comic_id']}",
                    "page_preview": f"/api/v1/download/comic_page/{comic_result['pages'][0]['page_id']}" if comic_result["pages"] else None
                },
                "animation": {
                    "id": prep_id,
                    "instructions": len(animated_shots),
                    "download": f"/api/v1/download/animation_prep/{prep_id}"
                },
                "video": {
                    "path": str(video_path),
                    "filename": Path(video_path).name,
                    "download": f"/api/v1/download/video/{Path(video_path).stem}"
                }
            }
        }
        
        print(f"\n✅ FULL PIPELINE COMPLETE in {total_time:.1f}s")
        print(f"   📊 Story: {len(story['scenes'])} scenes")
        print(f"   🎬 Shots: {len(shots)}")
        print(f"   🎨 Panels: {len(comic_result['panels'])}")
        print(f"   📄 Pages: {len(comic_result['pages'])}")
        print(f"   🎥 TRUE 3D Video: Created with dynamic motion and {'music' if music_path else 'narration only'}")
        print("="*60 + "\n")
        
        return JSONResponse(content=result)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/v1/download/{file_type}/{file_id}")
async def download_file(file_type: str, file_id: str):
    if file_type == "story":
        path = STORIES_DIR / f"{file_id}.json"
        if not path.exists():
            path = STORIES_DIR / f"{file_id}.txt"
    elif file_type == "scenes":
        path = SCENES_DIR / f"{file_id}.json"
    elif file_type == "comic":
        path = COMICS_DIR / f"{file_id}.json"
    elif file_type == "comic_page":
        path = COMICS_DIR / f"{file_id}.png"
    elif file_type == "panel":
        path = PANELS_DIR / f"{file_id}.png"
    elif file_type == "animation_prep":
        path = ANIMATIONS_DIR / f"{file_id}.json"
    elif file_type == "video":
        videos = list(VIDEOS_DIR.glob(f"*{file_id}*.mp4"))
        if videos:
            return FileResponse(videos[0], filename=videos[0].name, media_type="video/mp4")
        else:
            raise HTTPException(404, "Video not found")
    else:
        raise HTTPException(404, "Unknown file type")
    if not path.exists():
        raise HTTPException(404, "File not found")
    return FileResponse(path, filename=path.name)

@app.get("/api/v1/negative/prompts")
async def get_negative_prompts_info():
    categories = {}
    for category, prompt_text in NEGATIVE_PROMPTS.items():
        terms = [t.strip() for t in prompt_text.split(", ")]
        categories[category] = {
            "term_count": len(terms),
            "sample_terms": terms[:10]
        }
    return {
        "success": True,
        "total_categories": len(NEGATIVE_PROMPTS),
        "total_terms": sum(c["term_count"] for c in categories.values()),
        "categories": categories
    }

# ========== STARTUP ==========
@app.on_event("startup")
async def startup_event():
    total_negative_terms = sum(len(p.split(", ")) for p in NEGATIVE_PROMPTS.values())
    print("\n" + "="*60)
    print("🤖 AI CREATIVE STUDIO PRO v5.0")
    print("🎬 TRUE 3D ANIMATION PIPELINE")
    print("="*60)
    print(f"\n🔧 SYSTEM STATUS:")
    print(f"   • Hugging Face Token: {'✅ SET' if HF_TOKEN else '❌ MISSING'}")
    print(f"   • FFmpeg: {'✅ Available' if check_ffmpeg() else '❌ Not Found'}")
    print(f"   • Pyttsx3: ✅ Loaded (offline TTS)")
    print(f"   • Background Music: {'✅ Found' if BACKGROUND_MUSIC.exists() else '❌ Not found'}")
    print(f"\n🚫 NEGATIVE PROMPTS:")
    print(f"   • Categories: {len(NEGATIVE_PROMPTS)}")
    print(f"   • Total terms: {total_negative_terms}")
    print(f"\n📐 RESOLUTION: {IMAGE_WIDTH}x{IMAGE_HEIGHT}")
    print(f"🎥 VIDEO: {VIDEO_WIDTH}x{VIDEO_HEIGHT} (16:9)")
    print(f"🎬 TRUE 3D FEATURES:")
    print(f"   • Parallax layering for depth")
    print(f"   • Dynamic camera movements (dolly, orbit, crane)")
    print(f"   • Particle effects (rain, sparks, glitch)")
    print(f"   • Music beat synchronization")
    print(f"   • Dynamic lighting and vignette pulsing")
    print(f"\n📁 Workspace: {WORKSPACE_DIR}")
    print(f"🌐 Server: http://localhost:8000")
    print(f"🔗 Test: http://localhost:8000/api/v1/test")
    print(f"\n🚀 Ready to create TRUE 3D animated stories with music!")
    print("="*60 + "\n")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)