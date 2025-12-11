/**
 * JavaScript for Add FAQ page
 * Handles form submission and validation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const form = document.getElementById('addFaqForm');
    const questionInput = document.getElementById('question');
    const categorySelect = document.getElementById('category');
    const answerInput = document.getElementById('answer');
    const keywordsInput = document.getElementById('keywords');
    const tagsInput = document.getElementById('tags');
    const orderInput = document.getElementById('order');
    const statusSelect = document.getElementById('status');
    const relatedFaqsSelect = document.getElementById('related_faqs');
    
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
    if (typeof ClassicEditor !== 'undefined') {
        ClassicEditor
            .create(answerInput, {
                toolbar: ['heading', '|', 'bold', 'italic', 'link', 'bulletedList', 'numberedList', 'blockQuote', 'undo', 'redo'],
                placeholder: 'Nhập câu trả lời...'
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
            placeholder: 'Nhập từ khóa, phân tách bằng dấu phẩy'
        });
        
        // Initialize Select2 for tags
        $(tagsInput).select2({
            tags: true,
            tokenSeparators: [',', ' '],
            placeholder: 'Nhập tags, phân tách bằng dấu phẩy'
        });
        
        // Initialize Select2 for related FAQs
        $(relatedFaqsSelect).select2({
            placeholder: 'Chọn FAQ liên quan'
        });
    }
    
    // Auto generate keywords from question
    questionInput.addEventListener('blur', function() {
        if ($.fn.select2 && !$(keywordsInput).val()?.length) {
            const question = this.value.toLowerCase();
            const stopWords = ['là', 'và', 'hoặc', 'của', 'với', 'trong', 'nào', 'như', 'không', 'có', 'được', 'gì', 'tại', 'sao', 'khi', 'nếu', 'vì', 'tại sao', 'như thế nào', 'thì', 'ai', 'bao giờ', 'ở đâu'];
            
            // Remove punctuation and split into words
            const words = question
                .replace(/[.,?!;:'"()]/g, '')
                .split(/\s+/);
            
            // Filter out stop words and short words
            const keywords = words
                .filter(word => word.length > 3 && !stopWords.includes(word))
                .slice(0, 5); // Get top 5 keywords
            
            if (keywords.length > 0) {
                const newOptions = keywords.map(keyword => new Option(keyword, keyword, true, true));
                $(keywordsInput).append(newOptions).trigger('change');
            }
        }
    });
    
    // Word counter for answer
    if (answerInput && !window.ClassicEditor) {
        const counterElement = document.createElement('div');
        counterElement.className = 'text-muted small mt-1 text-right';
        counterElement.textContent = `0 ký tự`;
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
        
        try {
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang lưu...';
            submitBtn.disabled = true;

            // Prepare FAQ data
            const faqData = {
                question: questionInput.value,
                category_id: categorySelect.value,
                answer: answerInput.value,
                keywords: $(keywordsInput).val() ? $(keywordsInput).val().join(',') : '',
                order: parseInt(orderInput.value) || 0,
                status: statusSelect.value,
                tags: $(tagsInput).val() ? $(tagsInput).val().join(',') : '',
                related_faqs: $(relatedFaqsSelect).val() || [],
                views: parseInt(document.getElementById('views').value) || 0,
                helpful: parseInt(document.getElementById('helpful').value) || 0,
                not_helpful: parseInt(document.getElementById('not_helpful').value) || 0
            };

            console.log('Sending FAQ data:', faqData);

            // Send API request
            const response = await fetch('/faq/add_faqs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify([faqData]) // API expects an array of FAQs
            });

            const result = await response.json();

            if (response.ok) {
                alert('Thêm FAQ thành công!');
                window.location.href = '/faq/web';
            } else {
                throw new Error(result.detail?.message || result.message || 'Có lỗi xảy ra');
            }
        } catch (error) {
            console.error('Error submitting form:', error);
            alert(error.message || 'Có lỗi xảy ra khi thêm FAQ. Vui lòng thử lại');
        } finally {
            // Reset button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });
    
    // Reset form button handler
    const resetButton = document.querySelector('button[type="reset"]');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            validator.reset();
            
            // Reset Select2 components
            if ($.fn.select2) {
                $(keywordsInput).val(null).trigger('change');
                $(tagsInput).val(null).trigger('change');
                $(relatedFaqsSelect).val(null).trigger('change');
            }
            
            // Reset rich text editor
            if (window.CKEDITOR && CKEDITOR.instances.answer) {
                CKEDITOR.instances.answer.setData('');
            }
        });
    }
}); 