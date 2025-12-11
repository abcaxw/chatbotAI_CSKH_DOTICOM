/**
 * JavaScript for Edit FAQ page
 * Handles form submission and validation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const form = document.getElementById('editFaqForm');
    const questionInput = document.getElementById('question');
    const categorySelect = document.getElementById('category');
    const answerInput = document.getElementById('answer');
    const keywordsInput = document.getElementById('keywords');
    const tagsInput = document.getElementById('tags');
    const orderInput = document.getElementById('order');
    const statusSelect = document.getElementById('status');
    const relatedFaqsSelect = document.getElementById('related_faqs');
    const faqId = form.dataset.faqId;
    
    // Initialize form validation
    const validator = new FormValidator(form, {
        validateOnSubmit: true,
        validateOnChange: true,
        validateOnBlur: true,
        showErrorsImmediately: true
    });
    
    // Add custom validation rules
    validator.addField('question', ['required', 'minLength:10', 'maxLength:255'], {
        required: 'Vui lòng nhập câu hỏi',
        minLength: 'Câu hỏi phải có ít nhất 10 ký tự',
        maxLength: 'Câu hỏi không được vượt quá 255 ký tự'
    });
    
    validator.addField('category_id', ['required'], {
        required: 'Vui lòng chọn danh mục'
    });
    
    validator.addField('answer', ['required', 'minLength:20'], {
        required: 'Vui lòng nhập câu trả lời',
        minLength: 'Câu trả lời phải có ít nhất 20 ký tự'
    });
    
    validator.addField('order', ['numeric', 'min:0'], {
        numeric: 'Thứ tự hiển thị phải là số',
        min: 'Thứ tự hiển thị không được nhỏ hơn 0'
    });
    
    validator.addField('status', ['required'], {
        required: 'Vui lòng chọn trạng thái'
    });
    
    // Initialize rich text editor for answer if available
    let editor;
    if (typeof ClassicEditor !== 'undefined') {
        ClassicEditor
            .create(answerInput, {
                toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'undo', 'redo'],
                placeholder: 'Nhập câu trả lời...'
            })
            .then(newEditor => {
                editor = newEditor;
            })
            .catch(error => {
                console.error('Error initializing editor:', error);
            });
    }
    
    // Initialize Select2 for keywords
    if ($.fn.select2) {
        $(keywordsInput).select2({
            tags: true,
            tokenSeparators: [',', ' '],
            placeholder: 'Nhập từ khóa, phân tách bằng dấu phẩy',
            maximumSelectionLength: 10,
            language: {
                maximumSelected: function() {
                    return 'Bạn chỉ có thể chọn tối đa 10 từ khóa';
                }
            }
        });
        
        // Initialize Select2 for tags
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
        
        // Initialize Select2 for related FAQs
        $(relatedFaqsSelect).select2({
            placeholder: 'Chọn FAQ liên quan',
            maximumSelectionLength: 5,
            language: {
                maximumSelected: function() {
                    return 'Bạn chỉ có thể chọn tối đa 5 FAQ liên quan';
                }
            }
        });
    }
    
    // Auto generate keywords from question if keywords are empty
    const generateKeywords = () => {
        if ($.fn.select2 && $(keywordsInput).select2('data').length === 0) {
            // Simple keyword extraction algorithm
            const question = questionInput.value.toLowerCase();
            const stopWords = ['là', 'và', 'hoặc', 'của', 'với', 'trong', 'nào', 'như', 'không', 'có', 'được', 'gì', 'tại', 'sao', 'khi', 'nếu', 'vì', 'tại sao', 'như thế nào', 'thì', 'ai', 'bao giờ', 'ở đâu'];
            
            // Remove punctuation and split into words
            const words = question
                .replace(/[.,?!;:'"()]/g, '')
                .split(/\s+/);
            
            // Filter out stop words and short words
            const keywords = words
                .filter(word => word.length > 3 && !stopWords.includes(word))
                .slice(0, 5); // Get top 5 keywords
            
            // Add keywords to Select2
            if (keywords.length > 0) {
                const newOptions = keywords.map(keyword => new Option(keyword, keyword, true, true));
                $(keywordsInput).append(newOptions).trigger('change');
                return true;
            }
        }
        return false;
    };
    
    // Generate keywords button handler
    const generateKeywordsButton = document.querySelector('.btn-generate-keywords');
    if (generateKeywordsButton) {
        generateKeywordsButton.addEventListener('click', function(e) {
            e.preventDefault();
            if (generateKeywords()) {
                Utils.showToast('success', 'Đã tạo từ khóa từ câu hỏi');
            } else {
                Utils.showToast('info', 'Không thể tạo từ khóa hoặc từ khóa đã tồn tại');
            }
        });
    }
    
    // Word counter for answer
    if (answerInput && !window.ClassicEditor) {
        const maxLength = 2000;
        const currentLength = answerInput.value.length;
        
        const counterElement = document.createElement('div');
        counterElement.className = 'text-muted small mt-1 text-right';
        counterElement.textContent = `${currentLength} ký tự`;
        answerInput.parentNode.appendChild(counterElement);
        
        answerInput.addEventListener('input', function() {
            const currentLength = this.value.length;
            counterElement.textContent = `${currentLength} ký tự`;
            
            if (currentLength < 20) {
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
            Utils.showToast('error', 'Vui lòng kiểm tra lại thông tin FAQ');
            return;
        }
        
        try {
            Utils.showSpinner();
            
            // Prepare form data
            const formData = new FormData(form);
            
            // Get content from editor if available
            if (editor) {
                formData.set('answer', editor.getData());
            } else if (window.CKEDITOR && CKEDITOR.instances.answer) {
                formData.set('answer', CKEDITOR.instances.answer.getData());
            }
            
            // Convert keywords and tags from Select2 to array format if needed
            if ($.fn.select2) {
                if ($(keywordsInput).data('select2')) {
                    const keywords = $(keywordsInput).select2('data').map(item => item.text);
                    formData.delete('keywords');
                    keywords.forEach(keyword => formData.append('keywords[]', keyword));
                }
                
                if ($(tagsInput).data('select2')) {
                    const tags = $(tagsInput).select2('data').map(item => item.text);
                    formData.delete('tags');
                    tags.forEach(tag => formData.append('tags[]', tag));
                }
            }
            
            // Send API request to update FAQ
            const response = await fetch(`/api/faq/${faqId}`, {
                method: 'PUT',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                Utils.showToast('success', 'Cập nhật FAQ thành công');
                
                // Redirect to FAQ list page
                setTimeout(() => {
                    window.location.href = '/faq';
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
    
    // Delete FAQ button handler
    const deleteButton = document.querySelector('.btn-delete-faq');
    if (deleteButton) {
        deleteButton.addEventListener('click', async function(e) {
            e.preventDefault();
            
            if (!confirm('Bạn có chắc chắn muốn xóa FAQ này?')) {
                return;
            }
            
            try {
                Utils.showSpinner();
                
                const response = await fetch(`/api/faq/${faqId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    Utils.showToast('success', 'Xóa FAQ thành công');
                    
                    // Redirect to FAQ list page
                    setTimeout(() => {
                        window.location.href = '/faq';
                    }, 1500);
                } else {
                    Utils.showToast('error', result.message || 'Có lỗi xảy ra khi xóa FAQ');
                }
            } catch (error) {
                console.error('Error deleting FAQ:', error);
                Utils.showToast('error', 'Có lỗi xảy ra khi xóa FAQ');
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