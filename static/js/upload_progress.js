/**
 * FILE METADATA ANALYZER - ENHANCED JAVASCRIPT
 * Handles file upload progress, validation, and user feedback
 * with full accessibility support
 */

(function() {
    'use strict';

    // DOM Elements
    const fileInput = document.getElementById('file-input');
    const fileLabel = document.querySelector('.file-input-label');
    const fileSelected = document.getElementById('file-selected');
    const selectedFilename = document.getElementById('selected-filename');
    const uploadForm = document.getElementById('upload-form');
    const uploadBtn = document.getElementById('upload-btn');
    const loader = document.getElementById('loader');
    const progressBar = document.getElementById('progress-fill');
    const progressStatus = document.getElementById('progress-status');
    const viewDetailsBtn = document.getElementById('view-details-btn');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');

    // Configuration
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    const ALLOWED_TYPES = [
        'image/jpeg',
        'image/jpg', 
        'image/png',
        'image/gif',
        'image/webp',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    ];

    /**
     * Initialize event listeners
     */
    function init() {
        if (!fileInput) return;

        // File input change handler
        fileInput.addEventListener('change', handleFileSelect);
        
        // Drag and drop support
        fileLabel.addEventListener('dragover', handleDragOver);
        fileLabel.addEventListener('dragleave', handleDragLeave);
        fileLabel.addEventListener('drop', handleDrop);
        
        // Form submission
        if (uploadForm) {
            uploadForm.addEventListener('submit', handleFormSubmit);
        }

        // Check if file was already uploaded (server-side render)
        const uploadedFilename = document.getElementById('uploaded-filename');
        if (uploadedFilename) {
            simulateProcessing();
        }
    }

    /**
     * Handle file selection from input
     */
    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            validateAndDisplayFile(file);
        }
    }

    /**
     * Handle drag over event
     */
    function handleDragOver(event) {
        event.preventDefault();
        event.stopPropagation();
        fileLabel.style.borderColor = 'var(--color-primary)';
        fileLabel.style.background = 'var(--color-bg-primary)';
    }

    /**
     * Handle drag leave event
     */
    function handleDragLeave(event) {
        event.preventDefault();
        event.stopPropagation();
        fileLabel.style.borderColor = 'var(--color-border)';
        fileLabel.style.background = 'var(--color-bg-secondary)';
    }

    /**
     * Handle file drop
     */
    function handleDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        
        fileLabel.style.borderColor = 'var(--color-border)';
        fileLabel.style.background = 'var(--color-bg-secondary)';

        const files = event.dataTransfer.files;
        if (files.length > 0) {
            // Manually set the file to the input
            fileInput.files = files;
            validateAndDisplayFile(files[0]);
        }
    }

    /**
     * Validate and display selected file
     */
    function validateAndDisplayFile(file) {
        // Hide any previous errors
        hideError();

        // Validate file size
        if (file.size > MAX_FILE_SIZE) {
            showError(
                `File too large! Maximum size is ${MAX_FILE_SIZE / 1024 / 1024}MB. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB.`
            );
            clearFileInput();
            return;
        }

        // Validate file type
        if (!ALLOWED_TYPES.includes(file.type) && !file.name.match(/\.(jpg|jpeg|png|gif|webp|pdf|doc|docx|txt)$/i)) {
            showError(
                `Unsupported file type! Please upload an image, PDF, or document file.`
            );
            clearFileInput();
            return;
        }

        // Display selected file
        if (selectedFilename && fileSelected) {
            selectedFilename.textContent = file.name;
            fileSelected.classList.add('show');
            
            // Update upload button text
            if (uploadBtn) {
                uploadBtn.innerHTML = '<span aria-hidden="true">🔍</span><span>Analyze ' + file.name + '</span>';
            }
        }
    }

    /**
     * Handle form submission
     */
    function handleFormSubmit(event) {
        const file = fileInput.files[0];
        
        if (!file) {
            event.preventDefault();
            showError('Please select a file to upload.');
            return;
        }

        // Show loading state
        if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.innerHTML = '<span class="spinner" aria-hidden="true"></span><span>Uploading...</span>';
        }

        // Show loader
        if (loader) {
            loader.classList.add('show');
        }

        // Note: Actual upload happens via form submission
        // Progress simulation will occur on the results page
    }

    /**
     * Simulate processing (for after upload completes)
     */
    function simulateProcessing() {
        if (!loader || !progressBar || !viewDetailsBtn) return;

        loader.classList.add('show');
        viewDetailsBtn.classList.remove('show');

        let progress = 0;
        const interval = setInterval(function() {
            progress += 2;
            
            if (progress > 100) progress = 100;
            
            progressBar.style.width = progress + '%';
            
            // Update progress bar ARIA attributes
            const progressBarElement = document.querySelector('.progress-bar');
            if (progressBarElement) {
                progressBarElement.setAttribute('aria-valuenow', progress);
            }
            
            // Update screen reader status
            if (progressStatus) {
                progressStatus.textContent = 'Processing: ' + progress + '% complete';
            }

            if (progress >= 100) {
                clearInterval(interval);
                
                setTimeout(function() {
                    loader.classList.remove('show');
                    viewDetailsBtn.classList.add('show');
                    
                    // Announce completion to screen readers
                    if (progressStatus) {
                        progressStatus.textContent = 'Processing complete! File details are ready to view.';
                    }
                    
                    // Focus on the view details button for keyboard users
                    const detailsLink = document.getElementById('view-details-link');
                    if (detailsLink) {
                        detailsLink.focus();
                    }
                }, 300);
            }
        }, 50); // ~5 seconds total
    }

    /**
     * Show error message
     */
    function showError(message) {
        if (errorMessage && errorText) {
            errorText.textContent = message;
            errorMessage.classList.remove('hidden');
            
            // Scroll to error
            errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
            // Focus on error for screen readers
            errorMessage.focus();
        }
    }

    /**
     * Hide error message
     */
    function hideError() {
        if (errorMessage) {
            errorMessage.classList.add('hidden');
        }
    }

    /**
     * Clear file input
     */
    function clearFileInput() {
        if (fileInput) {
            fileInput.value = '';
        }
        if (fileSelected) {
            fileSelected.classList.remove('show');
        }
        if (uploadBtn) {
            uploadBtn.innerHTML = '<span aria-hidden="true">🔍</span><span>Analyze File</span>';
        }
    }

    /**
     * Format file size for display
     */
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Keyboard navigation improvements
     */
    function enhanceKeyboardNav() {
        // Make file label keyboard accessible
        if (fileLabel) {
            fileLabel.setAttribute('tabindex', '0');
            
            fileLabel.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    fileInput.click();
                }
            });
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            init();
            enhanceKeyboardNav();
        });
    } else {
        init();
        enhanceKeyboardNav();
    }

})();