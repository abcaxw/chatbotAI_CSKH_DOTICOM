/**
 * Form Validation Component
 * Provides client-side validation for forms
 */

class FormValidator {
    /**
     * Create a form validator
     * @param {HTMLFormElement|string} form - Form element or selector
     * @param {Object} options - Validation options
     */
    constructor(form, options = {}) {
        this.form = typeof form === 'string' ? document.querySelector(form) : form;
        if (!this.form || !(this.form instanceof HTMLFormElement)) {
            throw new Error('Invalid form element');
        }

        this.options = Object.assign({
            validateOnInput: true,
            validateOnBlur: true,
            validateOnSubmit: true,
            stopOnFirstError: false,
            errorClass: 'is-invalid',
            validClass: 'is-valid',
            errorElement: '.invalid-feedback',
            showValid: false
        }, options);

        this.validators = {};
        this.errorMessages = {};
        this.customValidators = {};

        // Regular expression patterns for common validations
        this.patterns = {
            email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
            url: /^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$/,
            phone: /^(\+84|84|0)[3|5|7|8|9][0-9]{8}$/,
            username: /^[a-zA-Z0-9_]{3,20}$/,
            password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$/,
            integer: /^-?\d+$/,
            decimal: /^-?\d+(\.\d+)?$/,
            alphanumeric: /^[a-zA-Z0-9]+$/,
            date: /^\d{4}-\d{2}-\d{2}$/
        };

        this.defaultMessages = {
            required: 'Trường này không được để trống',
            email: 'Vui lòng nhập địa chỉ email hợp lệ',
            url: 'Vui lòng nhập URL hợp lệ',
            phone: 'Vui lòng nhập số điện thoại hợp lệ',
            username: 'Tên người dùng chỉ được chứa chữ cái, số và dấu gạch dưới (3-20 ký tự)',
            password: 'Mật khẩu phải có ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường và số',
            minlength: (min) => `Vui lòng nhập ít nhất ${min} ký tự`,
            maxlength: (max) => `Vui lòng nhập không quá ${max} ký tự`,
            min: (min) => `Vui lòng nhập giá trị lớn hơn hoặc bằng ${min}`,
            max: (max) => `Vui lòng nhập giá trị nhỏ hơn hoặc bằng ${max}`,
            pattern: 'Vui lòng nhập đúng định dạng',
            match: 'Các trường không khớp',
            integer: 'Vui lòng nhập số nguyên',
            decimal: 'Vui lòng nhập số thập phân',
            alphanumeric: 'Vui lòng chỉ nhập chữ cái và số',
            date: 'Vui lòng nhập ngày hợp lệ (YYYY-MM-DD)'
        };

        this.initEvents();
        this.initBuiltInValidators();
    }

    /**
     * Initialize event listeners
     */
    initEvents() {
        if (this.options.validateOnSubmit) {
            this.form.addEventListener('submit', (e) => {
                if (!this.validate()) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Focus the first invalid field
                    const firstInvalid = this.form.querySelector(`.${this.options.errorClass}`);
                    if (firstInvalid) {
                        firstInvalid.focus();
                    }
                }
            });
        }

        if (this.options.validateOnInput) {
            this.form.addEventListener('input', (e) => {
                const field = e.target;
                if (field.name && this.validators[field.name]) {
                    this.validateField(field);
                }
            });
        }

        if (this.options.validateOnBlur) {
            this.form.addEventListener('blur', (e) => {
                const field = e.target;
                if (field.name && this.validators[field.name]) {
                    this.validateField(field);
                }
            }, true);
        }
    }

    /**
     * Initialize built-in validators
     */
    initBuiltInValidators() {
        this.addValidator('required', (value) => {
            return value !== null && value !== undefined && value.toString().trim() !== '';
        });

        this.addValidator('email', (value) => {
            return !value || this.patterns.email.test(value);
        });

        this.addValidator('url', (value) => {
            return !value || this.patterns.url.test(value);
        });

        this.addValidator('phone', (value) => {
            return !value || this.patterns.phone.test(value);
        });

        this.addValidator('minlength', (value, minLength) => {
            return !value || value.length >= minLength;
        });

        this.addValidator('maxlength', (value, maxLength) => {
            return !value || value.length <= maxLength;
        });

        this.addValidator('min', (value, min) => {
            return !value || parseFloat(value) >= min;
        });

        this.addValidator('max', (value, max) => {
            return !value || parseFloat(value) <= max;
        });

        this.addValidator('pattern', (value, pattern) => {
            return !value || new RegExp(pattern).test(value);
        });

        this.addValidator('match', (value, fieldName) => {
            const matchField = this.form.querySelector(`[name="${fieldName}"]`);
            return !value || !matchField || value === matchField.value;
        });

        this.addValidator('integer', (value) => {
            return !value || this.patterns.integer.test(value);
        });

        this.addValidator('decimal', (value) => {
            return !value || this.patterns.decimal.test(value);
        });

        this.addValidator('alphanumeric', (value) => {
            return !value || this.patterns.alphanumeric.test(value);
        });

        this.addValidator('date', (value) => {
            if (!value) return true;
            if (!this.patterns.date.test(value)) return false;
            
            const date = new Date(value);
            return !isNaN(date.getTime());
        });

        this.addValidator('username', (value) => {
            return !value || this.patterns.username.test(value);
        });

        this.addValidator('password', (value) => {
            return !value || this.patterns.password.test(value);
        });
    }

    /**
     * Add a validator
     * @param {string} name - Validator name
     * @param {Function} fn - Validator function
     */
    addValidator(name, fn) {
        this.customValidators[name] = fn;
    }

    /**
     * Add a rule for a field
     * @param {string} fieldName - Field name
     * @param {Object} rules - Validation rules
     * @param {Object} [messages] - Custom error messages
     */
    addField(fieldName, rules, messages = {}) {
        this.validators[fieldName] = rules;
        this.errorMessages[fieldName] = messages;
    }

    /**
     * Set rules for multiple fields
     * @param {Object} fields - Field rules {fieldName: {rules, messages}}
     */
    setFields(fields) {
        Object.entries(fields).forEach(([fieldName, config]) => {
            this.addField(fieldName, config.rules, config.messages || {});
        });
    }

    /**
     * Validate all form fields
     * @returns {boolean} - Whether the form is valid
     */
    validate() {
        let isValid = true;
        const fields = Object.keys(this.validators);

        fields.forEach(fieldName => {
            const fieldElements = this.form.querySelectorAll(`[name="${fieldName}"]`);
            if (fieldElements.length) {
                const fieldIsValid = this.validateField(fieldElements[0]);
                if (!fieldIsValid && isValid) {
                    isValid = false;
                }
                
                if (!fieldIsValid && this.options.stopOnFirstError) {
                    return false; // Break the loop
                }
            }
        });

        return isValid;
    }

    /**
     * Validate a specific field
     * @param {HTMLElement} field - Field element
     * @returns {boolean} - Whether the field is valid
     */
    validateField(field) {
        const fieldName = field.name;
        if (!fieldName || !this.validators[fieldName]) {
            return true;
        }

        const rules = this.validators[fieldName];
        const value = this.getFieldValue(field);
        
        this.clearFieldErrors(field);
        
        let isValid = true;
        
        // Process each validation rule
        for (const [ruleName, ruleValue] of Object.entries(rules)) {
            // Skip if rule is not active or not a validator
            if (!ruleValue || !this.customValidators[ruleName]) {
                continue;
            }
            
            const validator = this.customValidators[ruleName];
            const isValidForRule = validator(value, ruleValue === true ? undefined : ruleValue, field, this.form);
            
            if (!isValidForRule) {
                isValid = false;
                
                // Get error message
                let errorMessage = this.errorMessages[fieldName]?.[ruleName];
                if (!errorMessage) {
                    if (typeof this.defaultMessages[ruleName] === 'function') {
                        errorMessage = this.defaultMessages[ruleName](ruleValue);
                    } else {
                        errorMessage = this.defaultMessages[ruleName] || `Validation failed for ${ruleName}`;
                    }
                }
                
                this.showFieldError(field, errorMessage);
                break; // Show only one error at a time
            }
        }
        
        if (isValid && this.options.showValid) {
            this.showFieldValid(field);
        }
        
        return isValid;
    }

    /**
     * Get the value of a field
     * @param {HTMLElement} field - Field element
     * @returns {string|Array|null} - Field value
     */
    getFieldValue(field) {
        if (field.type === 'checkbox') {
            return field.checked;
        } else if (field.type === 'radio') {
            const checkedRadio = this.form.querySelector(`input[name="${field.name}"]:checked`);
            return checkedRadio ? checkedRadio.value : null;
        } else if (field.multiple) {
            const values = [];
            const options = field.selectedOptions;
            for (let i = 0; i < options.length; i++) {
                values.push(options[i].value);
            }
            return values;
        } else {
            return field.value;
        }
    }

    /**
     * Show error for a field
     * @param {HTMLElement} field - Field element
     * @param {string} message - Error message
     */
    showFieldError(field, message) {
        field.classList.add(this.options.errorClass);
        field.classList.remove(this.options.validClass);
        
        // Find or create error element
        let errorElement = this.getErrorElement(field);
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = this.options.errorElement.substring(1);
            field.parentNode.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
    }

    /**
     * Show valid state for a field
     * @param {HTMLElement} field - Field element
     */
    showFieldValid(field) {
        field.classList.add(this.options.validClass);
        field.classList.remove(this.options.errorClass);
        
        const errorElement = this.getErrorElement(field);
        if (errorElement) {
            errorElement.textContent = '';
        }
    }

    /**
     * Clear errors for a field
     * @param {HTMLElement} field - Field element
     */
    clearFieldErrors(field) {
        field.classList.remove(this.options.errorClass);
        field.classList.remove(this.options.validClass);
        
        const errorElement = this.getErrorElement(field);
        if (errorElement) {
            errorElement.textContent = '';
        }
    }

    /**
     * Get error element for a field
     * @param {HTMLElement} field - Field element
     * @returns {HTMLElement|null} - Error element
     */
    getErrorElement(field) {
        return field.parentNode.querySelector(this.options.errorElement);
    }

    /**
     * Reset the form and clear all errors
     */
    reset() {
        this.form.reset();
        
        Object.keys(this.validators).forEach(fieldName => {
            const fields = this.form.querySelectorAll(`[name="${fieldName}"]`);
            fields.forEach(field => {
                this.clearFieldErrors(field);
            });
        });
    }
}

// Make globally available
window.FormValidator = FormValidator; 