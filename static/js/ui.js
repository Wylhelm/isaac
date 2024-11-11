function initializeUI() {
    const createScenarioBtn = document.getElementById('createScenarioBtn');
    const darkModeToggle = document.getElementById('darkModeToggle');
    const criteriaTextarea = document.getElementById('criteria');
    const exportScenarioBtn = document.getElementById('exportScenario');
    const scenarioNameInput = document.getElementById('scenarioName');

    // Initialize form state
    scenarioNameInput.disabled = true;
    criteriaTextarea.disabled = true;
    exportScenarioBtn.disabled = true;

    // Initialize event listeners
    createScenarioBtn.addEventListener('click', handleCreateScenario);
    darkModeToggle.addEventListener('click', toggleDarkMode);
    criteriaTextarea.addEventListener('input', () => {
        toggleCriteriaPlaceholder();
        updateGenerateButton();
    });
    exportScenarioBtn.addEventListener('click', exportScenario);

    // Initialize placeholder visibility
    toggleCriteriaPlaceholder();

    // Initialize generate button state
    updateGenerateButton();
}

function handleCreateScenario() {
    // Enable form elements
    const scenarioNameInput = document.getElementById('scenarioName');
    const criteriaTextarea = document.getElementById('criteria');
    const fileUploadInput = document.getElementById('fileUpload');
    const generateButton = document.getElementById('generateButton');
    
    scenarioNameInput.disabled = false;
    criteriaTextarea.disabled = false;
    fileUploadInput.disabled = false;
    
    // Reset form
    document.getElementById('scenarioForm').reset();
    document.getElementById('scenarioForm').style.display = 'block';

    // Set new scenario name
    scenarioNameInput.value = `Scenario ${window.scenarioCounter || 1}`;
    window.scenarioCounter = (window.scenarioCounter || 1) + 1;

    // Clear UI elements
    document.getElementById('generatedScenario').textContent = '';
    document.getElementById('exportScenario').disabled = true;
    document.getElementById('fileList').innerHTML = '';

    // Update button states
    generateButton.textContent = 'Generate Scenario';
    generateButton.classList.remove('btn-success');
    generateButton.classList.add('btn-primary');
    generateButton.disabled = true;

    // Clear inference stats
    const inferenceStatsDiv = document.getElementById('inferenceStats');
    inferenceStatsDiv.textContent = '';
    inferenceStatsDiv.style.display = 'none';

    // Update placeholder and button states
    toggleCriteriaPlaceholder();
    updateGenerateButton();

    // Focus on scenario name input
    scenarioNameInput.focus();
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
    
    if (!criteria || !placeholder) return;
    
    const criteriaValue = criteria.value || '';
    placeholder.style.display = (criteriaValue.trim() === '' && !isFormActive) ? 'block' : 'none';
}

function updateGenerateButton() {
    const generateButton = document.getElementById('generateButton');
    const criteria = document.getElementById('criteria');
    
    if (!generateButton || !criteria) return;
    
    const criteriaValue = criteria.value || '';
    const isFormActive = !document.getElementById('scenarioName').disabled;
    
    if (criteriaValue.trim() === '' || !isFormActive) {
        generateButton.disabled = true;
        generateButton.classList.remove('btn-success', 'btn-primary');
        generateButton.classList.add('btn-secondary');
    } else {
        generateButton.disabled = false;
        if (generateButton.textContent === 'Generate Scenario') {
            generateButton.classList.remove('btn-secondary', 'btn-success');
            generateButton.classList.add('btn-primary');
        } else {
            generateButton.classList.remove('btn-secondary', 'btn-primary');
            generateButton.classList.add('btn-success');
        }
    }
}

function exportScenario() {
    const scenario = document.getElementById('generatedScenario').textContent;
    const scenarioName = document.getElementById('scenarioName').value || 'untitled';
    
    if (!scenario.trim()) {
        showAlert('No scenario content to export');
        return;
    }
    
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
