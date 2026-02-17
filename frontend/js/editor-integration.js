// Integration with Manga Editor Desu
class MangaEditorIntegration {
    constructor() {
        this.editor = null;
        this.isEditorLoaded = false;
        this.currentPage = null;
    }
    
    async loadEditor(containerId) {
        const container = document.getElementById(containerId);
        
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }
        
        // Create iframe for Manga Editor Desu
        const iframe = document.createElement('iframe');
        iframe.id = 'manga-editor-iframe';
        iframe.src = 'lib/manga-editor-desu/index.html'; // Path to Manga Editor Desu
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        
        container.innerHTML = '';
        container.appendChild(iframe);
        
        // Wait for iframe to load
        iframe.onload = () => {
            this.isEditorLoaded = true;
            this.editor = iframe.contentWindow;
            this.initializeEditorCommunication();
        };
        
        // Fallback if iframe fails to load
        setTimeout(() => {
            if (!this.isEditorLoaded) {
                this.showFallbackEditor(container);
            }
        }, 5000);
    }
    
    showFallbackEditor(container) {
        container.innerHTML = `
            <div class="h-full flex flex-col items-center justify-center p-8">
                <i class="fas fa-exclamation-triangle text-yellow-500 text-4xl mb-4"></i>
                <h3 class="text-xl font-bold text-gray-900 mb-2">Editor Load Failed</h3>
                <p class="text-gray-600 text-center mb-6">
                    Could not load Manga Editor Desu. Please ensure it's installed in the lib/manga-editor-desu directory.
                </p>
                <div class="flex space-x-4">
                    <a href="https://github.com/new-sankaku/manga-editor-desu" 
                       target="_blank" 
                       class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700">
                        Download Editor
                    </a>
                    <button onclick="window.app.useSimpleEditor()" 
                            class="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300">
                        Use Simple Editor
                    </button>
                </div>
            </div>
        `;
    }
    
    initializeEditorCommunication() {
        // Set up message passing between parent and iframe
        window.addEventListener('message', (event) => {
            this.handleEditorMessage(event.data);
        });
        
        // Send initialization message to editor
        this.sendToEditor({
            type: 'INIT',
            config: {
                apiEndpoint: 'http://localhost:8000/api/v1',
                projectId: window.app.currentProject?.id,
                enableAI: true
            }
        });
    }
    
    sendToEditor(message) {
        if (this.editor && this.isEditorLoaded) {
            this.editor.postMessage(message, '*');
        }
    }
    
    handleEditorMessage(message) {
        console.log('Editor message:', message);
        
        switch (message.type) {
            case 'READY':
                console.log('Manga Editor Desu is ready');
                break;
                
            case 'REQUEST_AI_GENERATION':
                this.handleAIGenerationRequest(message.data);
                break;
                
            case 'SAVE_PROJECT':
                this.saveEditorProject(message.data);
                break;
                
            case 'LOAD_PROJECT':
                this.loadEditorProject(message.projectId);
                break;
        }
    }
    
    async handleAIGenerationRequest(data) {
        const { prompt, type, options } = data;
        
        try {
            let result;
            
            switch (type) {
                case 'PANEL':
                    result = await window.apiClient.generateComicPanel(
                        prompt,
                        options?.artStyle || 'anime',
                        options?.composition
                    );
                    break;
                    
                case 'CHARACTER':
                    // Character generation logic
                    result = { image_url: 'https://placehold.co/400x600/4f46e5/ffffff?text=Character' };
                    break;
                    
                case 'BACKGROUND':
                    // Background generation logic
                    result = { image_url: 'https://placehold.co/800x600/7c3aed/ffffff?text=Background' };
                    break;
            }
            
            // Send result back to editor
            this.sendToEditor({
                type: 'AI_GENERATION_RESULT',
                data: {
                    originalRequest: data,
                    result: result
                }
            });
            
        } catch (error) {
            console.error('AI generation failed:', error);
            
            this.sendToEditor({
                type: 'AI_GENERATION_ERROR',
                data: {
                    originalRequest: data,
                    error: error.message
                }
            });
        }
    }
    
    async saveEditorProject(projectData) {
        // Save editor project to backend
        try {
            const response = await fetch('http://localhost:8000/api/v1/projects/editor/save', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(projectData)
            });
            
            const result = await response.json();
            
            this.sendToEditor({
                type: 'SAVE_RESULT',
                data: result
            });
            
        } catch (error) {
            console.error('Save failed:', error);
            
            this.sendToEditor({
                type: 'SAVE_ERROR',
                data: { error: error.message }
            });
        }
    }
    
    async loadEditorProject(projectId) {
        // Load project from backend
        try {
            const response = await fetch(`http://localhost:8000/api/v1/projects/editor/load/${projectId}`);
            const projectData = await response.json();
            
            this.sendToEditor({
                type: 'LOAD_RESULT',
                data: projectData
            });
            
        } catch (error) {
            console.error('Load failed:', error);
            
            this.sendToEditor({
                type: 'LOAD_ERROR',
                data: { error: error.message }
            });
        }
    }
    
    generatePanelFromScene(sceneData) {
        // Generate comic panel from scene data
        this.sendToEditor({
            type: 'GENERATE_PANEL_FROM_SCENE',
            data: sceneData
        });
    }
    
    addSpeechBubble(text, position, character) {
        // Add speech bubble to current panel
        this.sendToEditor({
            type: 'ADD_SPEECH_BUBBLE',
            data: { text, position, character }
        });
    }
    
    changeArtStyle(style) {
        // Change art style for generation
        this.sendToEditor({
            type: 'CHANGE_ART_STYLE',
            data: { style }
        });
    }
    
    exportPage(format = 'png') {
        // Export current page
        this.sendToEditor({
            type: 'EXPORT',
            data: { format }
        });
    }
}

// Simple fallback editor
class SimpleEditor {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.canvas = null;
        this.context = null;
        this.panels = [];
        this.currentTool = 'select';
        
        this.init();
    }
    
    init() {
        this.container.innerHTML = `
            <div class="h-full flex flex-col">
                <!-- Toolbar -->
                <div class="bg-gray-100 border-b border-gray-300 p-3 flex items-center space-x-4">
                    <div class="flex space-x-2">
                        <button class="editor-tool active" data-tool="select" title="Select">
                            <i class="fas fa-mouse-pointer"></i>
                        </button>
                        <button class="editor-tool" data-tool="panel" title="Add Panel">
                            <i class="fas fa-square"></i>
                        </button>
                        <button class="editor-tool" data-tool="text" title="Add Text">
                            <i class="fas fa-font"></i>
                        </button>
                        <button class="editor-tool" data-tool="bubble" title="Speech Bubble">
                            <i class="fas fa-comment"></i>
                        </button>
                    </div>
                    
                    <div class="flex-1"></div>
                    
                    <div class="flex space-x-2">
                        <button class="bg-indigo-600 text-white px-3 py-1 rounded text-sm" onclick="window.simpleEditor.generateAIPanel()">
                            <i class="fas fa-robot mr-1"></i> AI Panel
                        </button>
                        <button class="bg-gray-200 text-gray-700 px-3 py-1 rounded text-sm" onclick="window.simpleEditor.undo()">
                            <i class="fas fa-undo mr-1"></i> Undo
                        </button>
                        <button class="bg-gray-200 text-gray-700 px-3 py-1 rounded text-sm" onclick="window.simpleEditor.clear()">
                            <i class="fas fa-trash mr-1"></i> Clear
                        </button>
                    </div>
                </div>
                
                <!-- Canvas Container -->
                <div class="flex-1 relative overflow-auto bg-gray-50">
                    <canvas id="simple-editor-canvas" class="absolute"></canvas>
                </div>
                
                <!-- Properties Panel -->
                <div class="bg-white border-t border-gray-300 p-3" style="height: 120px;">
                    <h4 class="font-medium text-gray-900 mb-2">Properties</h4>
                    <div id="editor-properties">
                        <p class="text-gray-600 text-sm">Select an element to edit properties</p>
                    </div>
                </div>
            </div>
        `;
        
        this.setupCanvas();
        this.setupEventListeners();
    }
    
    setupCanvas() {
        this.canvas = document.getElementById('simple-editor-canvas');
        this.context = this.canvas.getContext('2d');
        
        // Set canvas size
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // Draw initial grid
        this.drawGrid();
    }
    
    resizeCanvas() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.clientWidth;
        this.canvas.height = container.clientHeight;
        this.drawGrid();
    }
    
    drawGrid() {
        const ctx = this.context;
        const width = this.canvas.width;
        const height = this.canvas.height;
        const gridSize = 20;
        
        ctx.clearRect(0, 0, width, height);
        
        // Draw grid
        ctx.strokeStyle = '#e5e7eb';
        ctx.lineWidth = 1;
        
        // Vertical lines
        for (let x = 0; x <= width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }
        
        // Draw existing panels
        this.panels.forEach(panel => this.drawPanel(panel));
    }
    
    drawPanel(panel) {
        const ctx = this.context;
        const { x, y, width, height } = panel;
        
        // Panel background
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(x, y, width, height);
        
        // Panel border
        ctx.strokeStyle = '#374151';
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, width, height);
        
        // Panel number
        ctx.fillStyle = '#6b7280';
        ctx.font = '14px Arial';
        ctx.fillText(`Panel ${panel.number}`, x + 10, y + 20);
        
        // If panel has image, draw it
        if (panel.imageUrl) {
            const img = new Image();
            img.onload = () => {
                ctx.drawImage(img, x + 10, y + 30, width - 20, height - 50);
            };
            img.src = panel.imageUrl;
        }
    }
    
    setupEventListeners() {
        // Tool selection
        document.querySelectorAll('.editor-tool').forEach(button => {
            button.addEventListener('click', (e) => {
                document.querySelectorAll('.editor-tool').forEach(btn => btn.classList.remove('active'));
                e.target.classList.add('active');
                this.currentTool = e.target.dataset.tool;
            });
        });
        
        // Canvas interactions
        this.canvas.addEventListener('click', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            switch (this.currentTool) {
                case 'panel':
                    this.addPanel(x, y);
                    break;
                case 'text':
                    this.addText(x, y);
                    break;
            }
        });
    }
    
    addPanel(x, y) {
        const panel = {
            id: Date.now(),
            number: this.panels.length + 1,
            x: Math.floor(x / 20) * 20,
            y: Math.floor(y / 20) * 20,
            width: 200,
            height: 150,
            imageUrl: null
        };
        
        this.panels.push(panel);
        this.drawGrid(); // Redraw with new panel
    }
    
    addText(x, y) {
        const text = prompt('Enter text:');
        if (text) {
            const ctx = this.context;
            ctx.fillStyle = '#000000';
            ctx.font = '16px Arial';
            ctx.fillText(text, x, y);
        }
    }
    
    async generateAIPanel() {
        const prompt = prompt('Describe the panel you want to generate:');
        if (!prompt) return;
        
        try {
            const result = await window.apiClient.generateComicPanel(prompt, 'anime');
            
            if (result.success && result.image_url) {
                // Add panel with generated image
                this.addPanel(100, 100);
                const lastPanel = this.panels[this.panels.length - 1];
                lastPanel.imageUrl = result.image_url;
                this.drawGrid();
                
                alert('AI panel generated successfully!');
            }
        } catch (error) {
            console.error('AI panel generation failed:', error);
            alert('Failed to generate panel: ' + error.message);
        }
    }
    
    undo() {
        if (this.panels.length > 0) {
            this.panels.pop();
            this.drawGrid();
        }
    }
    
    clear() {
        if (confirm('Clear all panels?')) {
            this.panels = [];
            this.drawGrid();
        }
    }
}

// Initialize editor integration
window.mangaEditor = new MangaEditorIntegration();
window.simpleEditor = null;

// Global function to use simple editor
window.app.useSimpleEditor = function() {
    window.simpleEditor = new SimpleEditor('editor-container');
};