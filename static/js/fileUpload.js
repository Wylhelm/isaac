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
        formData.append('files', files[i]);
        
        // Create and append list item
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.textContent = files[i].name;
        
        // Add analyzing indicator for images
        if (files[i].type.startsWith('image/')) {
            li.textContent += ' (Analyzing image...)';
        }
        
        fileList.appendChild(li);
    }

    try {
        // Upload files and get analysis results
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const data = await response.json();

        // Update file list and criteria textarea
        let newContent = criteriaTextarea.value;
        data.results.forEach((result, index) => {
            const li = fileList.children[fileList.children.length - files.length + index];
            
            // Update list item text
            if (li.textContent.includes('(Analyzing image...)')) {
                li.textContent = li.textContent.replace(' (Analyzing image...)', ' (Analysis complete)');
            }
            
            // Add file content to criteria
            newContent += `\n\nFile: ${result.filename}\n${result.content}`;
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
        showAlert('Failed to upload files. Please try again.');
        
        // Remove failed uploads from the list
        Array.from(files).forEach(() => {
            fileList.removeChild(fileList.lastChild);
        });
    }
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
