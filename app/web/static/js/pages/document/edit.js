/**
 * JavaScript for Edit Document page
 * Handles form submission, validation, and file upload
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const form = document.getElementById('editDocumentForm');
    const titleInput = document.getElementById('title');
    const categorySelect = document.getElementById('category');
    const descriptionInput = document.getElementById('description');
    const contentInput = document.getElementById('content');
    const tagsInput = document.getElementById('tags');
    const statusSelect = document.getElementById('status');
    const fileInput = document.getElementById('file');
    const thumbnailInput = document.getElementById('thumbnail');
    const relatedDocsSelect = document.getElementById('related_documents');
    const documentId = form.dataset.documentId;
    
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
    let editor;
    if (typeof ClassicEditor !== 'undefined') {
        ClassicEditor
            .create(contentInput, {
                toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'insertTable', 'undo', 'redo'],
                placeholder: 'Nhập nội dung tài liệu...'
            })
            .then(newEditor => {
                editor = newEditor;
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
        const fileName = this.files[0] ? this.files[0].name : 'Chọn file mới';
        this.nextElementSibling.textContent = fileName;
    });
    
    // Word counter for description
    if (descriptionInput) {
        const maxLength = 500;
        const currentLength = descriptionInput.value.length;
        
        const counterElement = document.createElement('div');
        counterElement.className = 'text-muted small mt-1 text-right';
        counterElement.textContent = `${currentLength}/${maxLength} ký tự`;
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
            
            // Get content from editor if available
            if (editor) {
                formData.set('content', editor.getData());
            } else if (window.CKEDITOR && CKEDITOR.instances.content) {
                formData.set('content', CKEDITOR.instances.content.getData());
            }
            
            // Convert tags from Select2 to array format if needed
            if ($.fn.select2 && $(tagsInput).data('select2')) {
                const tags = $(tagsInput).select2('data').map(item => item.text);
                formData.delete('tags');
                tags.forEach(tag => formData.append('tags[]', tag));
            }
            
            // Send API request to update document
            const response = await fetch(`/api/document/${documentId}`, {
                method: 'PUT',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                Utils.showToast('success', 'Cập nhật tài liệu thành công');
                
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
    
    // Delete document button handler
    const deleteButton = document.querySelector('.btn-delete-document');
    if (deleteButton) {
        deleteButton.addEventListener('click', async function(e) {
            e.preventDefault();
            
            if (!confirm('Bạn có chắc chắn muốn xóa tài liệu này?')) {
                return;
            }
            
            try {
                Utils.showSpinner();
                
                const response = await fetch(`/api/document/${documentId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    Utils.showToast('success', 'Xóa tài liệu thành công');
                    
                    // Redirect to document list page
                    setTimeout(() => {
                        window.location.href = '/document';
                    }, 1500);
                } else {
                    Utils.showToast('error', result.message || 'Có lỗi xảy ra khi xóa tài liệu');
                }
            } catch (error) {
                console.error('Error deleting document:', error);
                Utils.showToast('error', 'Có lỗi xảy ra khi xóa tài liệu');
            } finally {
                Utils.hideSpinner();
            }
        });
    }
    
    // Reset form button handler
    const resetButton = document.querySelector('button[type="reset"]');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            if (confirm('Bạn có chắc chắn muốn hủy các thay đổi?')) {
                window.location.reload();
            }
        });
    }
}); 