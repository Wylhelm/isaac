function initializeUI() {
    const createScenarioBtn = document.getElementById('createScenarioBtn');
    const darkModeToggle = document.getElementById('darkModeToggle');
    const criteriaTextarea = document.getElementById('criteria');
    const exportScenarioBtn = document.getElementById('exportScenario');

    // Initialize event listeners
    createScenarioBtn.addEventListener('click', handleCreateScenario);
    darkModeToggle.addEventListener('click', toggleDarkMode);
    criteriaTextarea.addEventListener('input', toggleCriteriaPlaceholder);
    exportScenarioBtn.addEventListener('click', exportScenario);

    // Initialize placeholder visibility
    toggleCriteriaPlaceholder();
}

function handleCreateScenario() {
    // Enable form elements
    document.getElementById('scenarioName').disabled = false;
    document.getElementById('criteria').disabled = false;
    document.getElementById('fileUpload').disabled = false;
    
    // Reset form
    document.getElementById('scenarioForm').reset();
    document.getElementById('scenarioForm').style.display = 'block';

    // Set new scenario name
    document.getElementById('scenarioName').value = `Scenario ${window.scenarioCounter}`;
    window.scenarioCounter++;

    // Clear UI elements
    document.getElementById('generatedScenario').textContent = '';
    document.getElementById('exportScenario').disabled = true;
    document.getElementById('fileList').innerHTML = '';

    // Update button states
    const generateButton = document.getElementById('generateButton');
    generateButton.textContent = 'Generate Scenario';
    generateButton.classList.remove('btn-success');
    generateButton.classList.add('btn-primary');

    // Clear inference stats
    const inferenceStatsDiv = document.getElementById('inferenceStats');
    inferenceStatsDiv.textContent = '';
    inferenceStatsDiv.style.display = 'none';

    // Update placeholder and button states
    toggleCriteriaPlaceholder();
    updateGenerateButton();

    // Focus on scenario name input
    document.getElementById('scenarioName').focus();
}

function toggleDarkMode() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    document.body.classList.toggle('dark-mode');
    
    if (document.body.classList.contains('dark-mode')) {
        darkModeToggle.textContent = 'Light Mode';
        darkModeToggle.classList.remove('btn-success');
        darkModeToggle.classList.add('btn-light');
    } else {
        darkModeToggle.textContent = 'Dark Mode';
        darkModeToggle.classList.remove('btn-light');
        darkModeToggle.classList.add('btn-success');
    }
}

function toggleCriteriaPlaceholder() {
    const criteria = document.getElementById('criteria');
    const placeholder = document.getElementById('criteriaPlaceholder');
    const isFormActive = !document.getElementById('scenarioName').disabled;
    
    placeholder.style.display = (criteria.value.trim() === '' && !isFormActive) ? 'block' : 'none';
}

function updateGenerateButton() {
    const generateButton = document.getElementById('generateButton');
    const criteria = document.getElementById('criteria').value.trim();
    
    if (criteria === '') {
        generateButton.disabled = true;
        generateButton.classList.remove('btn-success');
        generateButton.classList.add('btn-secondary');
    } else {
        generateButton.disabled = false;
        generateButton.classList.remove('btn-secondary');
        generateButton.classList.add('btn-success');
    }
}

function exportScenario() {
    const scenario = document.getElementById('generatedScenario').textContent;
    const scenarioName = document.getElementById('scenarioName').value;
    const blob = new Blob([scenario], {type: 'text/plain'});
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${scenarioName.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_scenario.txt`;
    a.click();
    
    URL.revokeObjectURL(url);
}

// Export functions that need to be globally accessible
window.initializeUI = initializeUI;
window.updateGenerateButton = updateGenerateButton;
window.toggleCriteriaPlaceholder = toggleCriteriaPlaceholder;
