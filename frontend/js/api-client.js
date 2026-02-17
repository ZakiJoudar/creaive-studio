// API Client for AI Creative Studio
class APIClient {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.storageKey = 'ai_studio_projects';
    }

    // Health check
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            return {
                status: 'offline',
                apis: { groq: 'offline', huggingface: 'offline' }
            };
        }
    }

    // Generate story
    async generateStory(prompt, genre = 'fantasy', style = 'anime', model = 'llama3-70b-8192') {
        const response = await fetch(`${this.baseURL}/api/v1/story/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt,
                genre,
                style,
                model
            })
        });
        return await response.json();
    }

    // Generate comic panel
    async generateComicPanel(sceneDescription, characters = [], location = '', mood = 'neutral', artStyle = 'anime') {
        const response = await fetch(`${this.baseURL}/api/v1/comic/generate-panel`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                scene_description: sceneDescription,
                characters,
                location,
                mood,
                art_style: artStyle
            })
        });
        return await response.json();
    }

    // Generate storyboard from story
    async generateStoryboard(storyId, artStyle = 'anime') {
        const response = await fetch(`${this.baseURL}/api/v1/comic/generate-storyboard`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                story_id: storyId,
                art_style: artStyle
            })
        });
        return await response.json();
    }

    // Prepare animation
    async prepareAnimation(storyboard, style = 'anime', fps = 24, duration = 60) {
        const response = await fetch(`${this.baseURL}/api/v1/animation/prepare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                storyboard,
                style,
                fps,
                duration
            })
        });
        return await response.json();
    }

    // Get system info
    async getSystemInfo() {
        const response = await fetch(`${this.baseURL}/api/v1/system/info`);
        return await response.json();
    }

    // List projects
    async listProjects() {
        const response = await fetch(`${this.baseURL}/api/v1/projects`);
        return await response.json();
    }

    // Save project locally
    saveProject(project) {
        const projects = this.getProjects();
        projects.push(project);
        localStorage.setItem(this.storageKey, JSON.stringify(projects));
    }

    // Get all projects from local storage
    getProjects() {
        return JSON.parse(localStorage.getItem(this.storageKey) || '[]');
    }

    // Clear all projects
    clearProjects() {
        localStorage.removeItem(this.storageKey);
    }
}

// Global API client instance
window.apiClient = new APIClient();