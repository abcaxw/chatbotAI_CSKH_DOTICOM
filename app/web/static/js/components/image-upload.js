/**
 * Image Upload Component
 * Provides image upload functionality with preview and validation
 */

class ImageUploader {
    /**
     * Create an image uploader
     * @param {HTMLElement|string} fileInput - File input element or selector
     * @param {Object} options - Configuration options
     */
    constructor(fileInput, options = {}) {
        this.fileInput = typeof fileInput === 'string' ? document.querySelector(fileInput) : fileInput;
        
        if (!this.fileInput || !(this.fileInput instanceof HTMLInputElement) || this.fileInput.type !== 'file') {
            throw new Error('Invalid file input element');
        }
        
        this.options = Object.assign({
            previewElement: null,
            previewClass: 'img-preview',
            dropZoneElement: null,
            dropZoneActiveClass: 'dropzone-active',
            maxFileSize: 5 * 1024 * 1024, // 5MB
            allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            imageWidth: null,
            imageHeight: null,
            useDataTransfer: true,
            crop: false,
            aspectRatio: null,
            errorElement: null,
            errorClass: 'is-invalid',
            errorMessageClass: 'invalid-feedback',
            onError: null,
            onSuccess: null,
            onChange: null,
            placeholder: '/images/cake-placeholder.png'
        }, options);
        
        // Create preview element if not provided
        if (!this.options.previewElement && this.options.previewClass) {
            this.options.previewElement = document.createElement('div');
            this.options.previewElement.className = this.options.previewClass;
            this.fileInput.parentNode.insertBefore(this.options.previewElement, this.fileInput.nextSibling);
        } else if (typeof this.options.previewElement === 'string') {
            this.options.previewElement = document.querySelector(this.options.previewElement);
        }
        
        // Create error message element if not provided
        if (!this.options.errorElement) {
            this.options.errorElement = document.createElement('div');
            this.options.errorElement.className = this.options.errorMessageClass;
            this.fileInput.parentNode.insertBefore(this.options.errorElement, this.fileInput.nextSibling);
        } else if (typeof this.options.errorElement === 'string') {
            this.options.errorElement = document.querySelector(this.options.errorElement);
        }
        
        // Setup drop zone if provided
        if (this.options.dropZoneElement) {
            if (typeof this.options.dropZoneElement === 'string') {
                this.options.dropZoneElement = document.querySelector(this.options.dropZoneElement);
            }
            this.setupDropZone();
        }
        
        // Set initial preview if file input has a value
        if (this.fileInput.dataset.initialPreview) {
            this.setPreview(this.fileInput.dataset.initialPreview);
        } else if (this.options.placeholder) {
            this.setPreview(this.options.placeholder);
        }
        
        this.setupEventListeners();
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Listen for file selection
        this.fileInput.addEventListener('change', (e) => {
            const files = e.target.files;
            if (files && files.length > 0) {
                this.handleFiles(files);
            }
        });
        
        // Clear errors when focusing the input
        this.fileInput.addEventListener('focus', () => {
            this.clearError();
        });
    }
    
    /**
     * Setup drop zone for drag and drop file uploads
     */
    setupDropZone() {
        const dropZone = this.options.dropZoneElement;
        
        if (!dropZone) return;
        
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });
        
        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add(this.options.dropZoneActiveClass);
            }, false);
        });
        
        // Remove highlight when item is dragged out or dropped
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove(this.options.dropZoneActiveClass);
            }, false);
        });
        
        // Handle dropped files
        dropZone.addEventListener('drop', (e) => {
            let files;
            if (this.options.useDataTransfer && e.dataTransfer) {
                files = e.dataTransfer.files;
            } else {
                files = e.target.files;
            }
            
            if (files && files.length > 0) {
                this.handleFiles(files);
            }
        }, false);
        
        // Allow clicking on the drop zone to trigger file input
        dropZone.addEventListener('click', () => {
            this.fileInput.click();
        });
    }
    
    /**
     * Handle files from input or drop
     * @param {FileList} files - The files to process
     */
    handleFiles(files) {
        const file = files[0]; // Only process the first file for now
        
        // Validate file
        const error = this.validateFile(file);
        if (error) {
            this.showError(error);
            if (typeof this.options.onError === 'function') {
                this.options.onError(error, file);
            }
            return;
        }
        
        // Clear any previous errors
        this.clearError();
        
        // Create preview
        this.createPreview(file);
        
        // Trigger onChange callback
        if (typeof this.options.onChange === 'function') {
            this.options.onChange(file);
        }
        
        // Trigger onSuccess callback
        if (typeof this.options.onSuccess === 'function') {
            this.options.onSuccess(file);
        }
    }
    
    /**
     * Validate a file
     * @param {File} file - The file to validate
     * @returns {string|null} - Error message or null if valid
     */
    validateFile(file) {
        // Check if file exists
        if (!file) {
            return 'Không có file nào được chọn';
        }
        
        // Check file type
        if (this.options.allowedTypes && this.options.allowedTypes.length > 0) {
            if (!this.options.allowedTypes.includes(file.type)) {
                return `Loại file không hợp lệ. Chỉ chấp nhận: ${this.options.allowedTypes.join(', ')}`;
            }
        }
        
        // Check file size
        if (this.options.maxFileSize && file.size > this.options.maxFileSize) {
            const maxSizeMB = Math.round(this.options.maxFileSize / (1024 * 1024) * 10) / 10;
            return `File quá lớn. Kích thước tối đa là ${maxSizeMB}MB`;
        }
        
        return null;
    }
    
    /**
     * Create image preview
     * @param {File} file - The file to preview
     */
    createPreview(file) {
        if (!this.options.previewElement) return;
        
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const previewUrl = e.target.result;
            
            // If dimensions validation is required, check the image
            if (this.options.imageWidth || this.options.imageHeight) {
                const img = new Image();
                img.onload = () => {
                    const widthValid = !this.options.imageWidth || img.width === this.options.imageWidth;
                    const heightValid = !this.options.imageHeight || img.height === this.options.imageHeight;
                    
                    if (!widthValid || !heightValid) {
                        let error = 'Kích thước ảnh không hợp lệ.';
                        if (this.options.imageWidth) {
                            error += ` Chiều rộng phải là ${this.options.imageWidth}px.`;
                        }
                        if (this.options.imageHeight) {
                            error += ` Chiều cao phải là ${this.options.imageHeight}px.`;
                        }
                        
                        this.showError(error);
                        if (typeof this.options.onError === 'function') {
                            this.options.onError(error, file);
                        }
                        return;
                    }
                    
                    this.setPreview(previewUrl);
                };
                
                img.onerror = () => {
                    this.showError('Không thể tải ảnh xem trước');
                };
                
                img.src = previewUrl;
            } else {
                this.setPreview(previewUrl);
            }
        };
        
        reader.onerror = () => {
            this.showError('Không thể đọc file');
        };
        
        reader.readAsDataURL(file);
    }
    
    /**
     * Set preview image
     * @param {string} src - The image source URL
     */
    setPreview(src) {
        if (!this.options.previewElement) return;
        
        const previewElement = this.options.previewElement;
        
        // Different behavior based on element type
        if (previewElement instanceof HTMLImageElement) {
            previewElement.src = src;
        } else {
            // Clear previous content
            previewElement.innerHTML = '';
            
            // Create image element
            const img = document.createElement('img');
            img.src = src;
            img.alt = 'Preview';
            img.style.maxWidth = '100%';
            
            previewElement.appendChild(img);
        }
    }
    
    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        // Add error class to input
        this.fileInput.classList.add(this.options.errorClass);
        
        // Display error message
        if (this.options.errorElement) {
            this.options.errorElement.textContent = message;
            this.options.errorElement.style.display = 'block';
        }
    }
    
    /**
     * Clear error message
     */
    clearError() {
        // Remove error class from input
        this.fileInput.classList.remove(this.options.errorClass);
        
        // Clear error message
        if (this.options.errorElement) {
            this.options.errorElement.textContent = '';
            this.options.errorElement.style.display = 'none';
        }
    }
    
    /**
     * Reset the uploader
     */
    reset() {
        // Clear file input
        this.fileInput.value = '';
        
        // Clear error
        this.clearError();
        
        // Reset preview to placeholder if available
        if (this.options.placeholder) {
            this.setPreview(this.options.placeholder);
        } else if (this.options.previewElement) {
            if (this.options.previewElement instanceof HTMLImageElement) {
                this.options.previewElement.src = '';
            } else {
                this.options.previewElement.innerHTML = '';
            }
        }
    }
    
    /**
     * Get the selected file
     * @returns {File|null} - Selected file or null
     */
    getFile() {
        return this.fileInput.files && this.fileInput.files.length > 0 ? this.fileInput.files[0] : null;
    }
}

// Make globally available
window.ImageUploader = ImageUploader; 