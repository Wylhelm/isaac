function initializeFileUpload() {
    const fileUpload = document.getElementById('fileUpload');
    fileUpload.addEventListener('change', handleFileUpload);
}

async function handleFileUpload(event) {
    const files = event.target.files;
    const formData = new FormData();
    const fileList = document.getElementById('fileList');
    const criteriaTextarea = document.getElementById('criteria');

    // Add files to form data and create list items
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file || !file.name) continue; // Skip invalid files
        
        formData.append('files', file);
        
        // Create and append list item with sanitized filename
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        // Create filename span
        const filenameSpan = document.createElement('span');
        filenameSpan.textContent = file.name.trim() || 'Unnamed file';
        li.appendChild(filenameSpan);
        
        // Add analyzing indicator for images
        if (file.type.startsWith('image/')) {
            const statusSpan = document.createElement('span');
            statusSpan.className = 'badge bg-info text-white';
            statusSpan.textContent = 'Analyzing image...';
            li.appendChild(statusSpan);
        }
        
        fileList.appendChild(li);
    }

    if (formData.getAll('files').length === 0) {
        showAlert('No valid files selected');
        return;
    }

    try {
        // Upload files and get analysis results
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        const data = await response.json();

        // Update file list and criteria textarea
        let newContent = criteriaTextarea.value;
        data.results.forEach((result, index) => {
            if (!result || !result.filename) return; // Skip invalid results
            
            // Find the last added list items
            const startIndex = fileList.children.length - files.length;
            const li = fileList.children[startIndex + index];
            if (!li) return; // Skip if list item doesn't exist
            
            // Update status badge if it exists
            const statusBadge = li.querySelector('.badge');
            if (statusBadge) {
                statusBadge.className = 'badge bg-success text-white';
                statusBadge.textContent = 'Analysis complete';
            }
            
            // Add file content to criteria
            newContent += `\n\nFile: ${result.filename}\n${result.content || ''}`;
        });

        // Update criteria textarea
        criteriaTextarea.value = newContent.trim();
        
        // Trigger input event to update placeholder and generate button
        criteriaTextarea.dispatchEvent(new Event('input'));
        
        // Scroll textarea to show new content
        criteriaTextarea.scrollTop = criteriaTextarea.scrollHeight;
        
        // Update UI states
        toggleCriteriaPlaceholder();
        updateGenerateButton();

    } catch (error) {
        console.error('File upload error:', error);
        showAlert(`Upload failed: ${error.message}`);
        
        // Update status badges to show error for the last added files
        const startIndex = fileList.children.length - files.length;
        for (let i = 0; i < files.length; i++) {
            const li = fileList.children[startIndex + i];
            if (li) {
                const statusBadge = li.querySelector('.badge');
                if (statusBadge) {
                    statusBadge.className = 'badge bg-danger text-white';
                    statusBadge.textContent = 'Upload failed';
                }
            }
        }
    }
}

// Function to clear the file input
function clearFileInput() {
    const fileUpload = document.getElementById('fileUpload');
    // Create a new file input element
    const newFileInput = document.createElement('input');
    newFileInput.type = 'file';
    newFileInput.id = fileUpload.id;
    newFileInput.name = fileUpload.name;
    newFileInput.className = fileUpload.className;
    newFileInput.multiple = fileUpload.multiple;
    newFileInput.accept = fileUpload.accept;
    
    // Copy event listeners
    newFileInput.addEventListener('change', handleFileUpload);
    
    // Replace the old input with the new one
    fileUpload.parentNode.replaceChild(newFileInput, fileUpload);
}

// Add drag and drop functionality
function initializeDragAndDrop() {
    const dropZone = document.getElementById('fileUpload');
    const dropZoneContainer = dropZone.parentElement;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZoneContainer.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZoneContainer.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZoneContainer.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZoneContainer.classList.add('drag-highlight');
    }

    function unhighlight() {
        dropZoneContainer.classList.remove('drag-highlight');
    }

    dropZoneContainer.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            document.getElementById('fileUpload').files = files;
            handleFileUpload({ target: { files: files } });
        }
    }
}

// Export functions that need to be globally accessible
window.initializeFileUpload = initializeFileUpload;
window.clearFileInput = clearFileInput;
