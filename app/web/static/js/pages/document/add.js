/**
 * JavaScript for Add Document page
 * Handles form submission, validation, and file upload
 */

// Load categories from API
async function loadCategories() {
    try {
        const response = await fetch('/category/get-categories', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        
        if (data.message === "Get categories successfully") {
            const categories = data.data;
            const categorySelect = document.getElementById('category_id');
            
            if (!categorySelect) {
                console.error('Category select element not found');
                return;
            }
            
            // Clear existing options
            categorySelect.innerHTML = '';
            
            // Add default option
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = 'Chọn danh mục';
            categorySelect.appendChild(defaultOption);
            
            // Add category options
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                categorySelect.appendChild(option);
            });
            
            // Initialize Select2
            $(categorySelect).select2({
                placeholder: 'Chọn danh mục',
                allowClear: true,
                width: '100%'
            });
        } else {
            console.error('Failed to load categories:', data.message);
            showError('Không thể tải danh mục. Vui lòng thử lại sau.');
        }
    } catch (error) {
        console.error('Error loading categories:', error);
        showError('Không thể tải danh mục. Vui lòng thử lại sau.');
    }
}

// Show error message
function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger';
    alertDiv.textContent = message;
    
    const form = document.querySelector('form');
    form.insertBefore(alertDiv, form.firstChild);
    
    // Remove alert after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const form = document.getElementById('addDocumentForm');
    const titleInput = document.getElementById('title');
    const categorySelect = document.getElementById('category');
    const descriptionInput = document.getElementById('description');
    const contentInput = document.getElementById('content');
    const tagsInput = document.getElementById('tags');
    const statusSelect = document.getElementById('status');
    const fileInput = document.getElementById('file');
    const thumbnailInput = document.getElementById('thumbnail');
    const relatedDocsSelect = document.getElementById('related_documents');
    
    // Initialize form validation
    const validator = new FormValidator(form, {
        validateOnSubmit: true,
        validateOnChange: true,
        validateOnBlur: true,
        showErrorsImmediately: true
    });
    
    // Add custom validation rules
    validator.addField('title', ['required', 'minLength:3', 'maxLength:200'], {
        required: 'Vui lòng nhập tiêu đề tài liệu',
        minLength: 'Tiêu đề phải có ít nhất 3 ký tự',
        maxLength: 'Tiêu đề không được vượt quá 200 ký tự'
    });
    
    validator.addField('category_id', ['required'], {
        required: 'Vui lòng chọn danh mục'
    });
    
    validator.addField('description', ['maxLength:500'], {
        maxLength: 'Mô tả không được vượt quá 500 ký tự'
    });
    
    validator.addField('status', ['required'], {
        required: 'Vui lòng chọn trạng thái'
    });
    
    validator.addValidator('fileType', function(value, fileInput) {
        if (!fileInput.files || fileInput.files.length === 0) {
            return true;
        }
        
        const file = fileInput.files[0];
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/zip',
            'application/x-rar-compressed'
        ];
        
        return allowedTypes.includes(file.type);
    });
    
    validator.addField('file', ['fileType'], {
        fileType: 'Định dạng file không được hỗ trợ'
    });
    
    // Initialize rich text editor for content
    if (typeof ClassicEditor !== 'undefined') {
        ClassicEditor
            .create(contentInput, {
                toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'insertTable', 'undo', 'redo'],
                placeholder: 'Nhập nội dung tài liệu...'
            })
            .catch(error => {
                console.error('Error initializing editor:', error);
            });
    }
    
    // Initialize image upload for thumbnail
    const thumbnailUploader = new ImageUploader('#thumbnail', {
        previewElement: '#thumbnailPreview',
        maxFileSize: 2 * 1024 * 1024, // 2MB
        allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        maxWidth: 800,
        maxHeight: 600,
        onValidationError: (message) => {
            validator.showFieldError(thumbnailInput, message);
        },
        onSuccess: () => {
            validator.clearFieldErrors(thumbnailInput);
        }
    });
    
    // Initialize Select2 for tags
    if ($.fn.select2) {
        $(tagsInput).select2({
            tags: true,
            tokenSeparators: [',', ' '],
            placeholder: 'Nhập tags, phân tách bằng dấu phẩy',
            maximumSelectionLength: 10,
            language: {
                maximumSelected: function() {
                    return 'Bạn chỉ có thể chọn tối đa 10 tags';
                }
            }
        });
        
        // Initialize Select2 for related documents
        $(relatedDocsSelect).select2({
            placeholder: 'Chọn tài liệu liên quan',
            maximumSelectionLength: 5,
            language: {
                maximumSelected: function() {
                    return 'Bạn chỉ có thể chọn tối đa 5 tài liệu liên quan';
                }
            }
        });
    }
    
    // Update file input label with selected filename
    fileInput.addEventListener('change', function() {
        const fileName = this.files[0] ? this.files[0].name : 'Chọn file';
        this.nextElementSibling.textContent = fileName;
    });
    
    // Word counter for description
    if (descriptionInput) {
        const maxLength = 500;
        const counterElement = document.createElement('div');
        counterElement.className = 'text-muted small mt-1 text-right';
        counterElement.textContent = `0/${maxLength} ký tự`;
        descriptionInput.parentNode.appendChild(counterElement);
        
        descriptionInput.addEventListener('input', function() {
            const currentLength = this.value.length;
            counterElement.textContent = `${currentLength}/${maxLength} ký tự`;
            
            if (currentLength > maxLength) {
                counterElement.classList.add('text-danger');
            } else {
                counterElement.classList.remove('text-danger');
            }
        });
    }
    
    // Form submission handler
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Validate form
        if (!validator.validate()) {
            Utils.showToast('error', 'Vui lòng kiểm tra lại thông tin tài liệu');
            return;
        }
        
        try {
            Utils.showSpinner();
            
            // Prepare form data
            const formData = new FormData(form);
            
            // Get content from CKEditor if available
            if (window.CKEDITOR && CKEDITOR.instances.content) {
                formData.set('content', CKEDITOR.instances.content.getData());
            }
            
            // Convert tags from Select2 to array format if needed
            if ($.fn.select2 && $(tagsInput).data('select2')) {
                const tags = $(tagsInput).select2('data').map(item => item.text);
                formData.delete('tags');
                tags.forEach(tag => formData.append('tags[]', tag));
            }
            
            // Send API request to create document
            const response = await fetch('/api/document', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                Utils.showToast('success', 'Thêm tài liệu thành công');
                
                // Redirect to document list page
                setTimeout(() => {
                    window.location.href = '/document';
                }, 1500);
            } else {
                Utils.showToast('error', result.message || 'Có lỗi xảy ra, vui lòng thử lại');
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            Utils.showToast('error', 'Có lỗi xảy ra, vui lòng thử lại');
        } finally {
            Utils.hideSpinner();
        }
    });
    
    // Reset form button handler
    const resetButton = document.querySelector('button[type="reset"]');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            validator.reset();
            thumbnailUploader.reset();
            
            // Reset Select2 components
            if ($.fn.select2) {
                $(tagsInput).val(null).trigger('change');
                $(relatedDocsSelect).val(null).trigger('change');
            }
            
            // Reset rich text editor
            if (window.CKEDITOR && CKEDITOR.instances.content) {
                CKEDITOR.instances.content.setData('');
            }
        });
    }

    // Load categories when page loads
    loadCategories();
}); 