document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('vcard-drop-zone');
    const fileList = document.getElementById('selected-files');
    const importForm = document.getElementById('import-vcard-form');
    const progressBar = document.getElementById('import-progress');
    const progressText = document.getElementById('progress-text');

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);

    function preventDefaults (e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function highlight(e) {
        dropZone.classList.add('drag-over');
    }

    function unhighlight(e) {
        dropZone.classList.remove('drag-over');
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFiles(files) {
        fileList.innerHTML = '';
        [...files].forEach(file => {
            if (file.name.toLowerCase().endsWith('.vcf')) {
                const li = document.createElement('li');
                li.className = 'selected-file';
                li.innerHTML = `
                    <i class="fas fa-address-card"></i>
                    <span>${file.name}</span>
                    <small>(${formatFileSize(file.size)})</small>
                `;
                fileList.appendChild(li);
            }
        });
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Handle form submission
    importForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(importForm);
        const files = document.querySelector('#vcard-file').files;
        
        if (files.length === 0) {
            showAlert('error', 'Please select at least one vCard file to import.');
            return;
        }

        // Add files to form data
        for (let i = 0; i < files.length; i++) {
            formData.append('vcard_files', files[i]);
        }

        // Debug: Log form data
        console.log('Form data:');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + (pair[1] instanceof File ? pair[1].name : pair[1]));
        }

        try {
            // Show progress bar
            progressBar.style.width = '0%';
            progressBar.parentElement.style.display = 'block';
            progressText.textContent = 'Starting import...';

            const response = await fetch('/contacts/import-vcard', {
                method: 'POST',
                body: formData
            });

            // Debug: Log response status
            console.log('Response status:', response.status);
            
            const result = await response.json();
            
            // Debug: Log response data
            console.log('Response data:', result);

            if (response.ok && result.success) {
                // Update progress bar to 100%
                progressBar.style.width = '100%';
                progressText.textContent = result.message;

                // Show success message with details
                showAlert('success', `
                    Import completed successfully:
                    - ${result.data.imported} contacts imported
                    - ${result.data.updated} contacts updated
                    - ${result.data.skipped} contacts skipped
                    ${result.data.errors.length > 0 ? '\nSome errors occurred:' : ''}
                    ${result.data.errors.join('\n')}
                `);

                // Clear file input and list
                document.querySelector('#vcard-file').value = '';
                fileList.innerHTML = '';

                // Reload contacts list if we're on the index page
                if (window.location.pathname === '/contacts') {
                    window.location.reload();
                }
            } else {
                // Handle error response
                let errorMessage = result.message || 'Unknown error occurred';
                if (result.data && result.data.errors && result.data.errors.length > 0) {
                    errorMessage += '\n\nErrors:\n' + result.data.errors.join('\n');
                }
                throw new Error(errorMessage);
            }
        } catch (error) {
            progressBar.style.width = '0%';
            progressText.textContent = 'Import failed';
            showAlert('error', 'Failed to import contacts: ' + error.message);
            
            // Log the full error for debugging
            console.error('Import error:', error);
        }
    });

    // File input change handler
    document.querySelector('#vcard-file').addEventListener('change', function(e) {
        handleFiles(e.target.files);
    });
});

function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        <div class="d-flex">
            <div class="me-3">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            </div>
            <div>
                ${message.replace(/\n/g, '<br>')}
            </div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.querySelector('.alert-container').appendChild(alertDiv);
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 10000);
} 