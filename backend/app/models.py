"""
DATA MODELS for AI Creative Studio
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

# ========== ENUMS ==========

class ArtStyle(str, Enum):
    MANGA = "manga"
    ANIME = "anime"
    COMIC = "comic"
    CYBERPUNK = "cyberpunk"
    FANTASY = "fantasy"
    SCI_FI = "sci_fi"
    REALISTIC = "realistic"
    CARTOON = "cartoon"

class Genre(str, Enum):
    SCI_FI = "sci_fi"
    CYBERPUNK = "cyberpunk"
    FANTASY = "fantasy"
    MYSTERY = "mystery"
    ADVENTURE = "adventure"
    ROMANCE = "romance"
    HORROR = "horror"
    COMEDY = "comedy"
    DRAMA = "drama"
    ACTION = "action"

class ContentRating(str, Enum):
    G = "G"
    PG = "PG"
    PG_13 = "PG-13"
    R = "R"
    NC_17 = "NC-17"

class AnimationStyle(str, Enum):
    TRADITIONAL = "traditional"
    CGI = "cgi"
    STOP_MOTION = "stop_motion"
    ANIME = "anime"
    CUTOUT = "cutout"
    CLAYMATION = "claymation"

# ========== BASE MODELS ==========

class Character(BaseModel):
    name: str
    age: Optional[int] = None
    role: str  # protagonist, antagonist, supporting, etc.
    personality: List[str] = []
    appearance: Dict[str, Any] = {}
    backstory: Optional[str] = None
    arc: Optional[str] = None

class Scene(BaseModel):
    scene_number: int
    title: str
    description: str
    location: str
    time_of_day: str = "day"
    characters: List[str] = []
    mood: str
    key_visual: str
    duration: str = "10 seconds"
    camera_angles: List[str] = []
    sound_design: Optional[str] = None
    dialogue: Optional[List[str]] = None
    actions: Optional[List[str]] = None

class Panel(BaseModel):
    panel_number: int
    scene_ref: int
    description: str
    composition: str
    characters: List[str] = []
    expressions: Dict[str, str] = {}  # character -> expression
    dialogue: Optional[str] = None
    sfx: Optional[str] = None  # sound effects
    camera_angle: str = "medium shot"

class ComicPage(BaseModel):
    page_number: int
    panels: List[Panel]
    layout: str  # e.g., "3-panel grid", "splash page"
    art_style: ArtStyle
    color_palette: Optional[List[str]] = None
    notes: Optional[str] = None

class AnimationFrame(BaseModel):
    frame_number: int
    timestamp: float  # seconds
    image_path: Optional[str] = None
    description: str
    camera: Dict[str, Any] = {}  # position, rotation, fov, etc.
    characters: Dict[str, Dict[str, Any]] = {}  # character -> pose data
    effects: List[str] = []

class AnimationScene(BaseModel):
    scene_number: int
    title: str
    frames: List[AnimationFrame]
    duration: float  # seconds
    fps: int = 24
    audio_track: Optional[str] = None
    transitions: List[str] = []  # cut, fade, dissolve, wipe, etc.

# ========== REQUEST MODELS ==========

class StoryRequest(BaseModel):
    premise: str = Field(..., min_length=10, max_length=1000)
    genre: Genre = Field(default=Genre.CYBERPUNK)
    art_style: ArtStyle = Field(default=ArtStyle.MANGA)
    length: str = Field(default="short", regex="^(short|medium|long|epic)$")
    main_character: Optional[str] = None
    supporting_characters: Optional[List[str]] = None
    setting: Optional[str] = None
    theme: Optional[str] = None
    tone: str = Field(default="serious", regex="^(serious|humorous|dark|lighthearted|epic|intimate)$")
    target_audience: ContentRating = Field(default=ContentRating.PG_13)
    additional_notes: Optional[str] = None

class ComicRequest(BaseModel):
    story_id: str
    art_style: ArtStyle = Field(default=ArtStyle.MANGA)
    num_pages: int = Field(default=3, ge=1, le=50)
    color: bool = Field(default=True)
    include_dialogue: bool = Field(default=True)
    panel_layout: str = Field(default="dynamic", regex="^(dynamic|grid|cinematic|manga)$")
    page_size: str = Field(default="comic", regex="^(comic|manga|webtoon|graphic_novel)$")

class AnimationRequest(BaseModel):
    comic_id: str
    animation_style: AnimationStyle = Field(default=AnimationStyle.ANIME)
    duration: int = Field(default=30, ge=5, le=600)  # seconds
    fps: int = Field(default=24, ge=1, le=60)
    resolution: str = Field(default="1080p", regex="^(480p|720p|1080p|2k|4k)$")
    include_audio: bool = Field(default=True)
    include_subtitles: bool = Field(default=False)
    output_format: str = Field(default="mp4", regex="^(mp4|avi|mov|webm|gif)$")

class GenerationConfig(BaseModel):
    use_flux: bool = Field(default=True)
    use_wan: bool = Field(default=True)
    hf_token: Optional[str] = None
    image_quality: str = Field(default="high", regex="^(low|medium|high|ultra)$")
    video_quality: str = Field(default="medium", regex="^(low|medium|high|ultra)$")
    batch_size: int = Field(default=1, ge=1, le=4)
    seed: Optional[int] = None
    safety_checker: bool = Field(default=True)
    nsfw_filter: bool = Field(default=True)

# ========== RESPONSE MODELS ==========

class StoryResponse(BaseModel):
    id: str
    premise: str
    genre: Genre
    title: Optional[str] = None
    logline: Optional[str] = None
    characters: List[Character] = []
    scenes: List[Scene] = []
    total_scenes: int
    estimated_length: str  # e.g., "30 minutes", "2 hours"
    themes: List[str] = []
    created_at: datetime
    art_style: ArtStyle
    status: str = "completed"

class ComicResponse(BaseModel):
    id: str
    story_id: str
    title: Optional[str] = None
    pages: List[ComicPage] = []
    total_pages: int
    art_style: ArtStyle
    color: bool
    layout: str
    generator: str
    created_at: datetime
    file_paths: Dict[str, str] = {}  # page_number -> image_path
    metadata: Dict[str, Any] = {}
    status: str = "completed"

class AnimationResponse(BaseModel):
    id: str
    comic_id: str
    title: Optional[str] = None
    scenes: List[AnimationScene] = []
    total_scenes: int
    total_duration: float
    total_frames: int
    fps: int
    resolution: str
    animation_style: AnimationStyle
    generator: str
    created_at: datetime
    file_paths: Dict[str, str] = {}  # scene_number -> video_path
    metadata: Dict[str, Any] = {}
    status: str = "completed"

class PipelineResponse(BaseModel):
    success: bool
    project_id: str
    pipeline: str
    time_taken: str
    components: Dict[str, Optional[str]]
    generators: Dict[str, str]
    files_generated: Dict[str, Optional[str]]
    workspace: str
    estimated_size: Optional[str] = None
    download_url: Optional[str] = None
    preview_url: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: Optional[str] = None
    suggestion: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# ========== DATABASE MODELS ==========

class Project(BaseModel):
    id: str
    title: str
    type: str  # story, comic, animation, complete
    description: Optional[str] = None
    story_id: Optional[str] = None
    comic_id: Optional[str] = None
    animation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime = Field(default_factory=datetime.now)
    status: str  # pending, processing, completed, failed
    config: Dict[str, Any] = {}
    tags: List[str] = []
    user_id: Optional[str] = None
    public: bool = Field(default=False)
    thumbnail: Optional[str] = None

class FileMetadata(BaseModel):
    id: str
    project_id: str
    file_type: str  # story, comic, animation, script, audio, etc.
    file_path: str
    file_name: str
    file_size: int  # bytes
    mime_type: str
    checksum: Optional[str] = None
    created_at: datetime
    modified_at: datetime = Field(default_factory=datetime.now)
    version: int = Field(default=1)
    metadata: Dict[str, Any] = {}
    access_level: str = Field(default="private", regex="^(private|shared|public)$")

class UserGenerationStats(BaseModel):
    user_id: str
    total_projects: int = 0
    total_stories: int = 0
    total_comics: int = 0
    total_animations: int = 0
    total_files: int = 0
    total_size: int = 0  # bytes
    credits_used: int = 0
    credits_remaining: int = 0
    last_generation: Optional[datetime] = None
    favorite_genres: List[str] = []
    favorite_styles: List[str] = []

# ========== UTILITY MODELS ==========

class ProgressUpdate(BaseModel):
    project_id: str
    stage: str
    progress: float  # 0.0 to 1.0
    message: str
    estimated_time_remaining: Optional[str] = None
    current_file: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class GeneratorStatus(BaseModel):
    flux_2: Dict[str, Any] = {
        "status": "ready",
        "version": "1.0",
        "capabilities": ["image_generation", "style_transfer"],
        "loaded": True
    }
    wan: Dict[str, Any] = {
        "status": "ready",
        "version": "1.0",
        "capabilities": ["video_generation", "animation"],
        "loaded": True
    }
    system: Dict[str, Any] = {
        "memory_available": 0,
        "gpu_available": False,
        "models_loaded": 0,
        "total_models": 2
    }
    last_updated: datetime = Field(default_factory=datetime.now)

# ========== EXPORT MODELS ==========

class ExportRequest(BaseModel):
    project_id: str
    format: str = Field(default="zip", regex="^(zip|tar|individual)$")
    include: List[str] = Field(default=["story", "comic", "animation"])
    quality: str = Field(default="original", regex="^(original|compressed|preview)$")
    watermark: bool = Field(default=False)
    metadata: bool = Field(default=True)

class ExportResponse(BaseModel):
    export_id: str
    project_id: str
    format: str
    file_size: int
    download_url: str
    expires_at: datetime
    checksum: str
    included_files: List[str]

# ========== VALIDATION FUNCTIONS ==========

def validate_story_request(request: StoryRequest) -> List[str]:
    """Validate story request and return any errors"""
    errors = []
    
    if len(request.premise) < 20:
        errors.append("Premise should be at least 20 characters")
    
    if request.genre == Genre.HORROR and request.target_audience == ContentRating.G:
        errors.append("Horror content should not be rated G")
    
    if request.tone == "humorous" and request.genre == Genre.HORROR:
        errors.append("Horror genre with humorous tone might not work well")
    
    return errors

def validate_comic_layout(layout: str, num_panels: int) -> bool:
    """Validate if layout can support number of panels"""
    layout_constraints = {
        "dynamic": (1, 12),
        "grid": (1, 9),
        "cinematic": (1, 6),
        "manga": (1, 8)
    }
    
    if layout in layout_constraints:
        min_panels, max_panels = layout_constraints[layout]
        return min_panels <= num_panels <= max_panels
    
    return False

def estimate_generation_time(request_type: str, config: Dict[str, Any]) -> int:
    """Estimate generation time in seconds"""
    base_times = {
        "story": 5,
        "comic_page": 30,
        "animation_second": 10
    }
    
    if request_type == "story":
        return base_times["story"]
    elif request_type == "comic":
        pages = config.get("num_pages", 3)
        return base_times["comic_page"] * pages
    elif request_type == "animation":
        duration = config.get("duration", 30)
        return base_times["animation_second"] * duration
    
    return 60  # default

# ========== EXAMPLE DATA ==========

def get_example_story_request() -> StoryRequest:
    """Get example story request"""
    return StoryRequest(
        premise="A cybernetic detective with memory implants investigates mysterious data thefts in Neo-Tokyo 2145. She discovers a rogue AI that erases painful memories, believing it's helping humanity.",
        genre=Genre.CYBERPUNK,
        art_style=ArtStyle.MANGA,
        main_character="Detective Aiko Tanaka",
        setting="Neo-Tokyo 2145, rain-soaked cyberpunk metropolis",
        theme="Memory, identity, and what it means to be human",
        tone="serious",
        target_audience=ContentRating.PG_13,
        additional_notes="Focus on noir detective elements with cyberpunk aesthetics"
    )

def get_example_scene() -> Scene:
    """Get example scene"""
    return Scene(
        scene_number=1,
        title="Rainy Night Investigation",
        description="Detective Aiko Tanaka arrives at a crime scene in the rain-drenched streets of Neo-Tokyo. Neon signs reflect in puddles as she examines a neural interface terminal.",
        location="Neon-lit alley in Shinjuku district",
        time_of_day="night",
        characters=["Aiko Tanaka"],
        mood="mysterious, tense, melancholic",
        key_visual="Aiko kneeling by glowing terminal, rain droplets on her cybernetic implants",
        duration="15 seconds",
        camera_angles=["Establishing wide shot of alley", "Close-up on terminal", "Low angle on Aiko"],
        sound_design="Ambient rain, distant city sounds, electronic hum from terminal, synth music cue"
    )

def get_example_panel() -> Panel:
    """Get example panel"""
    return Panel(
        panel_number=1,
        scene_ref=1,
        description="Aiko examines the neural interface, her cybernetic eye glowing as she accesses the data.",
        composition="Medium close-up, Aiko kneeling, terminal in foreground, rain visible in background",
        characters=["Aiko"],
        expressions={"Aiko": "focused, determined"},
        dialogue="AIKO: 'Another memory theft. Same pattern.'",
        sfx="*BEEP* *BEEP* (terminal sounds)",
        camera_angle="medium close-up"
    )