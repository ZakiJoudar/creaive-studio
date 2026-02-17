# AI Creative Studio Pro - Scalable Animation Pipeline

![AI Creative Studio Pro](https://img.shields.io/badge/version-4.1-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal)
![License](https://img.shields.io/badge/license-MIT-orange)

A powerful, scalable creative studio that transforms simple story premises into fully realized comic books and 3D animated videos using state-of-the-art AI models. This pipeline automates the entire creative process from story generation to final video production.

## 🎥 Demo

https://github.com/user-attachments/assets/your-demo-video-link

## ✨ Features

### 📖 Story Generation
- Generate structured stories with 3 cinematic scenes
- Support for multiple genres (Cyberpunk, Fantasy, Sci-Fi, Noir)
- Detailed scene descriptions with location, mood, and key actions
- JSON and human-readable text output formats

### 🎬 Intelligent Scene Segmentation
- Automatically breaks each scene into 4 detailed shots
- Shot types: Establishing, Medium, Close-up, Action
- Camera angles, composition notes, and timing for each shot
- 12+ total shots per complete story

### 🎨 Comic/Manga Creation
- AI-powered panel generation using Hugging Face models
- Comprehensive negative prompts (560+ terms) to avoid artifacts
- Multi-model fallback system (SDXL, SD 1.5, OpenJourney, FLUX)
- Manga-style page layouts (right-to-left) or Western layouts
- Individual panel storage and page composition

### 🎬 Animation Preparation
- Keyframe instructions for each shot
- Camera movement definitions (pan, zoom, shake, static)
- Character animation guidelines
- Particle effects for cyberpunk/action scenes
- Lip-sync detection for close-ups

### 🎥 3D Video Creation
- True 3D animated video with motion effects
- Ken Burns-style camera movements
- Particle effects based on genre
- Audio narration (offline TTS using pyttsx3)
- Background music support (MP3)
- FFmpeg-based encoding with fallback options

### 🛡️ Quality Control
- 560+ negative prompt terms across 6 categories
- Hand/arm anatomy enforcement
- Face/head detail preservation
- Image quality validation (rejects flat/generated images)
- Post-processing sharpening and contrast enhancement

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Story     │────▶│   Scene     │────▶│   Comic     │────▶│ Animation   │────▶│    Video    │
│ Generation  │     │ Segmentation │     │  Creation   │     │ Preparation │     │  Creation   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                    │                    │                    │                    │
      ▼                    ▼                    ▼                    ▼                    ▼
  JSON/TXT              JSON                  PNG/JSON              JSON                 MP4
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- FFmpeg (for video encoding)
- Hugging Face API token (for image generation)
- Windows/Linux/MacOS

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-creative-studio.git
   cd ai-creative-studio
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```



5. **Install FFmpeg**
   - **Windows**: Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add to PATH
   - **Linux**: `sudo apt install ffmpeg`
   - **Mac**: `brew install ffmpeg`

6. **Add background music (optional)**
   Place an MP3 file named `background_music.mp3` in the `backend/workspace/` directory

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000 --host 0.0.0.0
   ```

2. **Start the frontend server**
   ```bash
   cd frontend
   python -m http.server 3000
   ```

3. **Open your browser**
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
ai-creative-studio/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables
│   └── workspace/              # Generated files
│       ├── stories/            # Story JSON & text files
│       ├── scenes/             # Shot segmentation data
│       ├── panels/             # Individual panel images
│       ├── comics/             # Page layouts & metadata
│       ├── storyboard/         # Storyboard sequences
│       ├── videos/              # Rendered MP4 videos
│       ├── audio/               # Narration audio files
│       └── animations/          # Animation instructions
├── frontend/
│   └── index.html              # Web interface
└── README.md
```

## 📦 Dependencies

### Backend
```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
aiohttp==3.9.1
Pillow==10.1.0
python-dotenv==1.0.0
numpy==1.26.2
pyttsx3==2.90
```

## 🎯 Usage Examples

### Basic Story Premise
```
A cybernetic detective investigates memory thefts in Neo-Tokyo 2145. 
She discovers a conspiracy that threatens to unravel reality itself.
```

### Pipeline Output
- **Story**: 3 scenes with locations, mood, and key actions
- **Shots**: 12 detailed shots with camera angles
- **Comic**: 3 pages with 12 AI-generated panels
- **Video**: 39-second 3D animated video with narration and effects

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | System status |
| `/api/v1/test` | GET | Connection test |
| `/api/v1/story/generate` | POST | Generate story from premise |
| `/api/v1/scene/segment` | POST | Segment story into shots |
| `/api/v1/comic/generate` | POST | Generate comic panels |
| `/api/v1/animation/prepare` | POST | Prepare animation instructions |
| `/api/v1/video/create` | POST | Create animated video |
| `/api/v1/pipeline/full` | POST | Run complete pipeline |
| `/api/v1/download/{type}/{id}` | GET | Download generated files |
| `/api/v1/negative/prompts` | GET | Get negative prompt info |

## ⚙️ Configuration Options

### Image Settings
- `IMAGE_WIDTH`: 768px (default)
- `IMAGE_HEIGHT`: 768px (default)
- `VIDEO_WIDTH`: 1280px (16:9)
- `VIDEO_HEIGHT`: 720px (16:9)
- `FPS`: 30 frames per second

### Quality Parameters
- Inference steps: 30
- Guidance scale: 7.5
- Negative prompt length: 1500 characters
- Retry attempts: 2 per model

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Hugging Face](https://huggingface.co/) for inference API
- [Stable Diffusion](https://stability.ai/) for image generation models
- [FFmpeg](https://ffmpeg.org/) for video encoding
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [TailwindCSS](https://tailwindcss.com/) for the frontend styling

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/ai-creative-studio](https://github.com/yourusername/ai-creative-studio)

## 🚀 Future Roadmap

- [ ] Integration with more image models (DALL-E, Midjourney)
- [ ] Custom training for character consistency
- [ ] Voice cloning for narration
- [ ] Multi-language support
- [ ] Cloud deployment (AWS, GCP, Azure)
- [ ] Mobile app version
- [ ] Collaborative editing features
- [ ] Export to multiple video formats
- [ ] Direct social media sharing

---

**Made with ❤️ by the AI Creative Studio Team**

