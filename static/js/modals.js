function initializeModals() {
    document.getElementById('editSystemPromptBtn').addEventListener('click', () => showPromptModal('system'));
    document.getElementById('editScenarioPromptBtn').addEventListener('click', () => showPromptModal('scenario'));
    document.getElementById('editContextWindowBtn').addEventListener('click', showContextWindowModal);
}

async function showPromptModal(type) {
    try {
        const endpoint = type === 'system' ? '/get_system_prompt' : '/get_scenario_prompt';
        const response = await fetch(endpoint);
        const data = await response.json();
        
        const modal = createModal({
            title: `Edit ${type.charAt(0).toUpperCase() + type.slice(1)} Prompt`,
            content: createTextArea(data.prompt),
            onSave: async (value) => {
                await savePrompt(type, value);
                removeModal(modal);
                showAlert(`${type.charAt(0).toUpperCase() + type.slice(1)} prompt updated successfully`);
            }
        });

        document.body.appendChild(modal);
    } catch (error) {
        console.error(`Error loading ${type} prompt:`, error);
        showAlert(`Failed to load ${type} prompt`);
    }
}

async function showContextWindowModal() {
    try {
        const response = await fetch('/get_context_window');
        const data = await response.json();
        
        const select = document.createElement('select');
        select.className = 'form-select mb-3';
        select.innerHTML = `
            <option value="4096" ${data.size === 4096 ? 'selected' : ''}>4096</option>
            <option value="8192" ${data.size === 8192 ? 'selected' : ''}>8192</option>
        `;

        const modal = createModal({
            title: 'Edit Context Window Size',
            content: select,
            onSave: async (value) => {
                await saveContextWindow(parseInt(value));
                removeModal(modal);
                showAlert(`Context window size set to ${value}`);
            }
        });

        document.body.appendChild(modal);
    } catch (error) {
        console.error('Error loading context window size:', error);
        showAlert('Failed to load context window size');
    }
}

async function savePrompt(type, prompt) {
    const endpoint = type === 'system' ? '/set_system_prompt' : '/set_scenario_prompt';
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({prompt})
        });
        
        if (!response.ok) {
            throw new Error(`Failed to save ${type} prompt`);
        }
    } catch (error) {
        console.error(`Error saving ${type} prompt:`, error);
        throw error;
    }
}

async function saveContextWindow(size) {
    try {
        const response = await fetch('/set_context_window', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({size})
        });
        
        if (!response.ok) {
            throw new Error('Failed to save context window size');
        }
    } catch (error) {
        console.error('Error saving context window size:', error);
        throw error;
    }
}

function createModal({title, content, onSave}) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    const modalContent = document.createElement('div');
    modalContent.className = 'modal-content';
    
    const titleElement = document.createElement('h4');
    titleElement.textContent = title;
    titleElement.className = 'mb-3';
    
    const saveBtn = document.createElement('button');
    saveBtn.textContent = 'Save';
    saveBtn.className = 'btn btn-primary me-2';
    
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel';
    cancelBtn.className = 'btn btn-secondary';
    
    modalContent.appendChild(titleElement);
    modalContent.appendChild(content);
    modalContent.appendChild(saveBtn);
    modalContent.appendChild(cancelBtn);
    modal.appendChild(modalContent);
    
    saveBtn.addEventListener('click', () => {
        onSave(content.value || content.selectedOptions[0].value);
    });
    
    cancelBtn.addEventListener('click', () => {
        removeModal(modal);
    });
    
    return modal;
}

function createTextArea(value) {
    const textarea = document.createElement('textarea');
    textarea.className = 'modal-textarea form-control';
    textarea.value = value;
    return textarea;
}

function removeModal(modal) {
    document.body.removeChild(modal);
}

// Export functions that need to be globally accessible
window.initializeModals = initializeModals;
