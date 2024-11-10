let abortController;

function initializeScenarioHandling() {
    const scenarioForm = document.getElementById('scenarioForm');
    const generateButton = document.getElementById('generateButton');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');

    scenarioForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await generateScenario();
        await loadScenarios();
    });

    generateButton.addEventListener('click', async () => {
        if (generateButton.textContent === 'Regenerate Scenario') {
            await generateScenario(true);
            await loadScenarios();
        }
    });

    clearHistoryBtn.addEventListener('click', clearHistory);
    document.getElementById('stopGeneration').addEventListener('click', stopGeneration);
}

function formatScenarioText(text) {
    // Remove excessive blank lines (more than 2 consecutive newlines)
    text = text.replace(/\n{3,}/g, '\n\n');
    
    // Ensure proper spacing after punctuation
    text = text.replace(/([.!?])\s*(\w)/g, '$1 $2');
    
    // Add proper indentation for lists
    text = text.replace(/^(-|\d+\.)\s*/gm, '  $1 ');
    
    // Ensure consistent spacing around sections
    text = text.replace(/^(#{1,6})\s*(.+)$/gm, '\n$1 $2\n');
    
    // Clean up any trailing/leading whitespace
    text = text.trim();
    
    return text;
}

async function generateScenario(isRegenerate = false) {
    const name = document.getElementById('scenarioName').value;
    const criteria = document.getElementById('criteria').value;
    const uploadedFiles = Array.from(document.getElementById('fileList').children).map(li => li.textContent);
    const generatedScenarioDiv = document.getElementById('generatedScenario');
    const inferenceStatsDiv = document.getElementById('inferenceStats');
    const generateButton = document.getElementById('generateButton');
    const stopButton = document.getElementById('stopGeneration');
    const exportButton = document.getElementById('exportScenario');
    
    // Reset UI state
    generatedScenarioDiv.textContent = '';
    inferenceStatsDiv.style.display = 'none';
    exportButton.disabled = true;
    stopButton.style.display = 'inline-block';
    generateButton.disabled = true;

    abortController = new AbortController();
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name, criteria, uploaded_files: uploadedFiles, is_regenerate: isRegenerate}),
            signal: abortController.signal
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        let fullContent = '';
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            fullContent += chunk;
        
            if (fullContent.includes('\n\nInference Statistics:')) {
                const [scenarioContent, stats] = fullContent.split('\n\nInference Statistics:');
                generatedScenarioDiv.textContent = formatScenarioText(scenarioContent);
                inferenceStatsDiv.textContent = 'Inference Statistics:\n' + stats;
                inferenceStatsDiv.style.display = 'block';
            } else {
                generatedScenarioDiv.textContent = formatScenarioText(fullContent);
            }
            
            generatedScenarioDiv.scrollTop = generatedScenarioDiv.scrollHeight;
        }

        // Update UI after successful generation
        exportButton.disabled = false;
        exportButton.classList.remove('btn-secondary');
        exportButton.classList.add('btn-success');
        
        generateButton.textContent = 'Regenerate Scenario';
        generateButton.classList.remove('btn-primary');
        generateButton.classList.add('btn-success');
        generateButton.disabled = false;

    } catch (error) {
        if (error.name === 'AbortError') {
            generatedScenarioDiv.textContent += '\n\nScenario generation stopped by user.';
        } else {
            console.error('Fetch error:', error);
            generatedScenarioDiv.textContent += '\n\nAn error occurred during scenario generation.';
        }
    } finally {
        stopButton.style.display = 'none';
        generateButton.disabled = false;
    }
}

async function loadScenarios() {
    try {
        const response = await fetch('/scenarios');
        const scenarios = await response.json();
        const historyDiv = document.getElementById('scenarioHistory');
        
        historyDiv.innerHTML = '';
        scenarios.forEach(scenario => {
            const div = document.createElement('div');
            div.className = 'history-item';
            div.innerHTML = `
                <strong>${scenario.name}</strong>
                <p class="mb-1">${formatScenarioText(scenario.scenario.substring(0, 100))}...</p>
                <small class="d-block">Files: ${scenario.uploaded_files || 'None'}</small>
                <small class="d-block text-muted">${scenario.statistics || ''}</small>
            `;
            
            div.addEventListener('click', () => loadScenario(scenario));
            historyDiv.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading scenarios:', error);
        showAlert('Failed to load scenario history');
    }
}

function loadScenario(scenario) {
    // Update form fields
    document.getElementById('scenarioName').value = scenario.name;
    document.getElementById('criteria').value = scenario.criteria;
    document.getElementById('generatedScenario').textContent = scenario.scenario ? formatScenarioText(scenario.scenario) : 'No scenario content available.';
    document.getElementById('exportScenario').disabled = false;
    
    // Update inference stats
    const inferenceStatsDiv = document.getElementById('inferenceStats');
    inferenceStatsDiv.textContent = scenario.statistics || '';
    inferenceStatsDiv.style.display = scenario.statistics ? 'block' : 'none';
    
    // Update file list
    document.getElementById('fileList').innerHTML = scenario.uploaded_files ? 
        scenario.uploaded_files.split(', ').map(file => 
            `<li class="list-group-item">${file}</li>`
        ).join('') : '';
    
    // Enable form elements
    document.getElementById('scenarioName').disabled = false;
    document.getElementById('criteria').disabled = false;
    document.getElementById('fileUpload').disabled = false;
    
    // Update generate button
    const generateButton = document.getElementById('generateButton');
    generateButton.textContent = 'Regenerate Scenario';
    generateButton.classList.remove('btn-primary');
    generateButton.classList.add('btn-success');
    generateButton.disabled = false;
    
    // Hide criteria placeholder
    document.getElementById('criteriaPlaceholder').style.display = 'none';
    
    updateGenerateButton();
    
    // Scroll to the top of the generated scenario
    const generatedScenarioDiv = document.getElementById('generatedScenario');
    generatedScenarioDiv.scrollTop = 0;
}

async function clearHistory() {
    if (confirm('Are you sure you want to clear all scenario history? This action cannot be undone.')) {
        try {
            const response = await fetch('/clear_history', { method: 'POST' });
            if (response.ok) {
                document.getElementById('scenarioHistory').innerHTML = '';
                showAlert('Scenario history has been cleared.');
            } else {
                showAlert('Failed to clear scenario history. Please try again.');
            }
        } catch (error) {
            console.error('Error clearing history:', error);
            showAlert('An error occurred while clearing the history. Please try again.');
        }
    }
}

function stopGeneration() {
    if (abortController) {
        abortController.abort();
    }
}

// Export functions that need to be globally accessible
window.initializeScenarioHandling = initializeScenarioHandling;
window.loadScenarios = loadScenarios;
