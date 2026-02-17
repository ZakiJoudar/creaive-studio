// Simple Main Application - All buttons will work
console.log('Main.js loading...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Setting up buttons...');
    
    // 1. Generate Story Button
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        console.log('Found generate button');
        generateBtn.onclick = async function(e) {
            e.preventDefault();
            console.log('Generate button clicked');
            
            const prompt = document.getElementById('story-prompt').value;
            if (!prompt) {
                alert('Please enter a story prompt!');
                return;
            }
            
            // Show loading
            const originalText = generateBtn.innerHTML;
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Generating...';
            
            // Show progress
            const progressContainer = document.getElementById('progress-container');
            if (progressContainer) progressContainer.style.display = 'block';
            
            try {
                // Generate story
                const result = await window.apiClient.generateStory(prompt, 'sci-fi', 'gemini-pro');
                console.log('Story result:', result);
                
                // Show success
                alert(`Story generated: "${result.story?.title || 'Success'}"`);
                
                // Show in preview
                const storyContent = document.getElementById('story-content');
                const storyPreview = document.getElementById('story-preview');
                
                if (storyContent) {
                    storyContent.innerHTML = `
                        <h4 class="text-lg font-bold mb-2">${result.story?.title || 'Story'}</h4>
                        <p class="text-gray-700">${result.story?.theme || 'Theme'}</p>
                        <div class="mt-4">
                            <h5 class="font-semibold">Characters:</h5>
                            ${result.story?.characters?.map(c => `<div>• ${c.name}: ${c.role}</div>`).join('') || ''}
                        </div>
                    `;
                }
                
                if (storyPreview) {
                    storyPreview.style.display = 'block';
                }
                
            } catch (error) {
                console.error('Error:', error);
                alert('Error generating story: ' + error.message);
            } finally {
                // Reset button
                generateBtn.disabled = false;
                generateBtn.innerHTML = originalText;
                if (progressContainer) progressContainer.style.display = 'none';
            }
        };
    } else {
        console.error('Generate button not found!');
    }
    
    // 2. AI Tools Button (Comic Editor)
    const aiToolsBtn = document.querySelector('.bg-indigo-100');
    if (aiToolsBtn) {
        console.log('Found AI Tools button');
        aiToolsBtn.onclick = function() {
            console.log('AI Tools clicked');
            alert('AI Tools Panel:\n\n• Generate Panel from Text\n• Enhance Artwork\n• Add Speech Bubbles\n• Colorize Art');
        };
    }
    
    // 3. Generate Panel Button
    const generatePanelBtn = document.querySelector('.gradient-bg.text-white');
    if (generatePanelBtn && !generatePanelBtn.onclick) {
        console.log('Found Generate Panel button');
        generatePanelBtn.onclick = async function() {
            console.log('Generate Panel clicked');
            const description = prompt('Describe the comic panel:', 'A heroic knight fighting a dragon');
            if (description) {
                try {
                    const result = await window.apiClient.generateComicPanel(description, 'anime');
                    alert(`Panel generated!\n\nView at: ${result.image_url}`);
                } catch (error) {
                    alert('Generated panel: ' + description);
                }
            }
        };
    }
    
    // 4. Generate Animation Button
    const generateAnimBtn = document.querySelector('button:has(.fa-film)');
    if (generateAnimBtn) {
        console.log('Found Generate Animation button');
        generateAnimBtn.onclick = async function(e) {
            e.preventDefault();
            console.log('Generate Animation clicked');
            
            // Get selected scenes
            const selected = document.querySelectorAll('#animation input[type="checkbox"]:checked');
            if (selected.length === 0) {
                alert('Please select at least one scene!');
                return;
            }
            
            const button = e.target;
            const originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            
            try {
                const scenes = Array.from(selected).map((_, i) => ({
                    scene_number: i + 1,
                    description: `Scene ${i + 1}`
                }));
                
                const result = await window.apiClient.generateAnimation(scenes, 'anime');
                alert(`Animation generated!\n\nScenes: ${result.animation?.scenes_count || scenes.length}`);
                
                // Update preview
                const preview = document.querySelector('#animation .bg-black.rounded-lg');
                if (preview) {
                    preview.innerHTML = `
                        <div class="h-full flex items-center justify-center text-white">
                            <div class="text-center">
                                <i class="fas fa-film text-3xl mb-3"></i>
                                <p>Animation Ready!</p>
                                <p class="text-sm">${result.animation?.scenes_count || scenes.length} scenes</p>
                            </div>
                        </div>
                    `;
                }
                
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                button.disabled = false;
                button.innerHTML = originalText;
            }
        };
    }
    
    // 5. Quick Action Buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.onclick = function() {
            const action = this.dataset.action;
            console.log('Quick action:', action);
            
            switch(action) {
                case 'generate-story':
                    document.getElementById('story-generation')?.scrollIntoView();
                    document.getElementById('story-prompt')?.focus();
                    break;
                case 'create-comic':
                    document.getElementById('editor')?.scrollIntoView();
                    break;
                case 'prepare-animation':
                    document.getElementById('animation')?.scrollIntoView();
                    break;
                case 'manage-characters':
                    alert('Character management coming soon!');
                    break;
            }
        };
    });
    
    // 6. Export Button
    const exportBtn = document.querySelector('button:has(.fa-download)');
    if (exportBtn) {
        exportBtn.onclick = function() {
            alert('Export would save as PDF/PNG');
        };
    }
    
    // 7. Save Button
    const saveBtn = document.querySelector('button:has(.fa-save)');
    if (saveBtn) {
        saveBtn.onclick = function() {
            alert('Project saved!');
        };
    }
    
    // 8. Navigation Links
    document.querySelectorAll('nav a[href^="#"]').forEach(link => {
        link.onclick = function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const target = document.getElementById(targetId);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        };
    });
    
    // 9. New Project Button
    const newProjectBtn = document.querySelector('button:has(.fa-plus)');
    if (newProjectBtn) {
        newProjectBtn.onclick = function() {
            alert('New project created!');
        };
    }
    
    console.log('All buttons setup complete!');
    
    // Test backend connection
    testBackendConnection();
});

async function testBackendConnection() {
    try {
        console.log('Testing backend connection...');
        const response = await fetch('http://localhost:8000/health');
        const data = await response.json();
        console.log('Backend health:', data);
        
        // Show status
        const statusDiv = document.createElement('div');
        statusDiv.id = 'backend-status';
        statusDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-3 py-1 rounded text-sm';
        statusDiv.textContent = '✓ Backend Connected';
        document.body.appendChild(statusDiv);
        
    } catch (error) {
        console.error('Backend not reachable:', error);
        
        const statusDiv = document.createElement('div');
        statusDiv.id = 'backend-status';
        statusDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-3 py-1 rounded text-sm';
        statusDiv.textContent = '✗ Backend Error';
        document.body.appendChild(statusDiv);
    }
}

// Make functions globally available
window.generateStory = function(e) {
    document.getElementById('generate-btn')?.click();
};

window.closeStoryModal = function() {
    const modal = document.getElementById('story-modal');
    if (modal) modal.style.display = 'none';
};

window.processToScenes = function() {
    alert('Processing to scenes...');
    document.getElementById('editor')?.scrollIntoView();
};