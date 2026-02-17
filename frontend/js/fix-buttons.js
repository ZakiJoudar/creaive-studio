// Quick fix for all buttons - add this to your index.html or main.js

function fixAllButtons() {
    console.log('Fixing all buttons...');
    
    // Fix AI Tools button
    const aiToolsBtn = document.querySelector('.bg-indigo-100.text-indigo-700');
    if (aiToolsBtn) {
        aiToolsBtn.onclick = () => {
            alert('AI Tools Panel\n\nAvailable features:\n1. Generate Panel from Text\n2. Enhance Artwork\n3. Generate Speech Bubbles\n4. Colorize Art\n\nIn a real implementation, this would open a tool panel.');
        };
    }
    
    // Fix Generate Panel button
    const generatePanelBtn = document.querySelector('.gradient-bg.text-white');
    if (generatePanelBtn && !generatePanelBtn.onclick) {
        generatePanelBtn.onclick = async () => {
            const prompt = prompt('Describe the comic panel you want to generate:',
                'A heroic knight standing before a dragon, dramatic lighting, fantasy style');
            if (prompt) {
                try {
                    const response = await fetch('http://localhost:8000/api/v1/comic/generate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({scene_description: prompt, art_style: 'anime'})
                    });
                    const result = await response.json();
                    alert(`✅ Panel generated!\n\nDescription: ${prompt}\nImage: ${result.image_url}`);
                } catch (error) {
                    alert(`Generated panel for: "${prompt}"\n\nIn a real app, this would call the AI image generator.`);
                }
            }
        };
    }
    
    // Fix Generate Animation button
    const animationBtns = document.querySelectorAll('button');
    animationBtns.forEach(btn => {
        if (btn.textContent.includes('Generate Animation') || 
            (btn.onclick && btn.onclick.toString().includes('generateAnimation'))) {
            btn.onclick = () => {
                const selected = document.querySelectorAll('#animation input[type="checkbox"]:checked').length;
                if (selected === 0) {
                    alert('Please select at least one scene for animation!');
                    return;
                }
                alert(`🎬 Generating animation from ${selected} scenes...\n\nThis would use AnimateDiff or similar AI animation models to create a video from your comic panels.`);
                
                // Update the preview
                const preview = document.querySelector('#animation .bg-black.rounded-lg');
                if (preview) {
                    preview.innerHTML = `
                        <div style="text-align: center; padding: 20px; color: white;">
                            <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                            <p>Generating Animation...</p>
                            <p class="text-sm">Processing ${selected} scenes</p>
                            <p class="text-xs mt-3">Using AI animation models to create smooth motion</p>
                        </div>
                    `;
                    
                    // Simulate completion after 3 seconds
                    setTimeout(() => {
                        preview.innerHTML = `
                            <video controls autoplay style="width: 100%; height: 100%;">
                                <source src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4" type="video/mp4">
                            </video>
                            <p style="color: white; text-align: center; font-size: 12px; padding: 5px;">
                                Demo Animation - Your AI-generated animation would appear here
                            </p>
                        `;
                    }, 3000);
                }
            };
        }
    });
    
    // Fix Export and Save buttons
    document.querySelectorAll('button').forEach(btn => {
        if (btn.textContent.includes('Export') && btn.querySelector('.fa-download')) {
            btn.onclick = () => alert('Export would save your comic as PDF/PNG files.');
        }
        if (btn.textContent.includes('Save') && btn.querySelector('.fa-save')) {
            btn.onclick = () => alert('Save would store your project to the database.');
        }
    });
    
    console.log('Buttons fixed!');
}

// Run when page loads
document.addEventListener('DOMContentLoaded', fixAllButtons);

// Also run after a short delay in case dynamic content loads later
setTimeout(fixAllButtons, 1000);