/**
 * Utility JavaScript functions for the application
 * Contains commonly used functions for DOM manipulation, data formatting, and other utilities
 */

// DOM Utilities
const DOM = {
    /**
     * Select an element from the DOM
     * @param {string} selector - CSS selector
     * @param {Element} [parent=document] - Parent element to search within
     * @returns {Element|null} - The selected element or null
     */
    select: (selector, parent = document) => parent.querySelector(selector),

    /**
     * Select multiple elements from the DOM
     * @param {string} selector - CSS selector
     * @param {Element} [parent=document] - Parent element to search within
     * @returns {NodeList} - The selected elements
     */
    selectAll: (selector, parent = document) => parent.querySelectorAll(selector),

    /**
     * Create a new element with optional attributes and content
     * @param {string} tag - Tag name
     * @param {Object} [attributes={}] - HTML attributes
     * @param {string|Element|Array} [content] - Inner content
     * @returns {Element} - The created element
     */
    create: (tag, attributes = {}, content) => {
        const element = document.createElement(tag);
        
        // Add attributes
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'class' || key === 'className') {
                if (Array.isArray(value)) {
                    element.classList.add(...value.filter(Boolean));
                } else if (typeof value === 'string') {
                    element.classList.add(...value.split(' ').filter(Boolean));
                }
            } else if (key === 'style' && typeof value === 'object') {
                Object.assign(element.style, value);
            } else if (key.startsWith('data-')) {
                element.setAttribute(key, value);
            } else if (key.startsWith('on') && typeof value === 'function') {
                element.addEventListener(key.substring(2).toLowerCase(), value);
            } else {
                element[key] = value;
            }
        });
        
        // Add content
        if (content !== undefined) {
            if (Array.isArray(content)) {
                content.forEach(item => {
                    if (item instanceof Element) {
                        element.appendChild(item);
                    } else {
                        element.appendChild(document.createTextNode(String(item)));
                    }
                });
            } else if (content instanceof Element) {
                element.appendChild(content);
            } else {
                element.textContent = String(content);
            }
        }
        
        return element;
    },

    /**
     * Add event listener to element(s)
     * @param {string|Element|NodeList} selector - CSS selector or element(s)
     * @param {string} event - Event name
     * @param {Function} callback - Event handler
     * @param {Object} [options] - Event options
     */
    on: (selector, event, callback, options) => {
        if (typeof selector === 'string') {
            DOM.selectAll(selector).forEach(el => {
                el.addEventListener(event, callback, options);
            });
        } else if (selector instanceof Element) {
            selector.addEventListener(event, callback, options);
        } else if (selector instanceof NodeList) {
            selector.forEach(el => {
                el.addEventListener(event, callback, options);
            });
        }
    },

    /**
     * Toggle class on element(s)
     * @param {string|Element|NodeList} selector - CSS selector or element(s)
     * @param {string} className - Class to toggle
     * @param {boolean} [force] - Force add or remove
     */
    toggleClass: (selector, className, force) => {
        if (typeof selector === 'string') {
            DOM.selectAll(selector).forEach(el => {
                el.classList.toggle(className, force);
            });
        } else if (selector instanceof Element) {
            selector.classList.toggle(className, force);
        } else if (selector instanceof NodeList) {
            selector.forEach(el => {
                el.classList.toggle(className, force);
            });
        }
    },

    /**
     * Add class to element(s)
     * @param {string|Element|NodeList} selector - CSS selector or element(s)
     * @param {string} className - Class to add
     */
    addClass: (selector, className) => {
        DOM.toggleClass(selector, className, true);
    },

    /**
     * Remove class from element(s)
     * @param {string|Element|NodeList} selector - CSS selector or element(s)
     * @param {string} className - Class to remove
     */
    removeClass: (selector, className) => {
        DOM.toggleClass(selector, className, false);
    }
};

// Storage Utilities
const Storage = {
    /**
     * Set item in localStorage with expiry
     * @param {string} key - Storage key
     * @param {*} value - Value to store
     * @param {number} [ttl] - Time to live in milliseconds
     */
    set: (key, value, ttl) => {
        const item = {
            value,
            expiry: ttl ? Date.now() + ttl : null
        };
        localStorage.setItem(key, JSON.stringify(item));
    },

    /**
     * Get item from localStorage
     * @param {string} key - Storage key
     * @param {*} [defaultValue] - Default value if key doesn't exist
     * @returns {*} - Stored value or default
     */
    get: (key, defaultValue = null) => {
        const itemStr = localStorage.getItem(key);
        
        if (!itemStr) {
            return defaultValue;
        }
        
        try {
            const item = JSON.parse(itemStr);
            
            if (item.expiry && Date.now() > item.expiry) {
                localStorage.removeItem(key);
                return defaultValue;
            }
            
            return item.value;
        } catch (e) {
            console.error('Error parsing stored item:', e);
            return defaultValue;
        }
    },

    /**
     * Remove item from localStorage
     * @param {string} key - Storage key
     */
    remove: (key) => {
        localStorage.removeItem(key);
    },

    /**
     * Clear all items from localStorage
     */
    clear: () => {
        localStorage.clear();
    }
};

// URL Utilities
const URL = {
    /**
     * Get URL parameters as an object
     * @returns {Object} - URL parameters
     */
    getParams: () => {
        const params = {};
        const searchParams = new URLSearchParams(window.location.search);
        
        for (const [key, value] of searchParams.entries()) {
            params[key] = value;
        }
        
        return params;
    },

    /**
     * Get a specific URL parameter
     * @param {string} name - Parameter name
     * @param {*} [defaultValue] - Default value if parameter doesn't exist
     * @returns {string|*} - Parameter value or default
     */
    getParam: (name, defaultValue = null) => {
        const params = URL.getParams();
        return name in params ? params[name] : defaultValue;
    },

    /**
     * Update or add URL parameters
     * @param {Object} params - Parameters to update
     * @param {boolean} [replace=false] - Whether to replace current history state
     */
    updateParams: (params, replace = false) => {
        const url = new URL(window.location.href);
        
        Object.entries(params).forEach(([key, value]) => {
            if (value === null || value === undefined) {
                url.searchParams.delete(key);
            } else {
                url.searchParams.set(key, value);
            }
        });
        
        if (replace) {
            window.history.replaceState({}, '', url);
        } else {
            window.history.pushState({}, '', url);
        }
    }
};

// Date Utilities
const DateUtils = {
    /**
     * Format date to locale string
     * @param {Date|string|number} date - Date to format
     * @param {Object} [options] - Intl.DateTimeFormat options
     * @param {string} [locale='vi-VN'] - Locale
     * @returns {string} - Formatted date
     */
    format: (date, options = { dateStyle: 'medium' }, locale = 'vi-VN') => {
        if (!date) return '';
        
        const dateObj = date instanceof Date ? date : new Date(date);
        
        if (isNaN(dateObj.getTime())) {
            console.error('Invalid date:', date);
            return '';
        }
        
        return new Intl.DateTimeFormat(locale, options).format(dateObj);
    },

    /**
     * Format relative time (e.g., "2 hours ago")
     * @param {Date|string|number} date - Date to format
     * @param {string} [locale='vi-VN'] - Locale
     * @returns {string} - Relative time
     */
    formatRelative: (date, locale = 'vi-VN') => {
        if (!date) return '';
        
        const dateObj = date instanceof Date ? date : new Date(date);
        
        if (isNaN(dateObj.getTime())) {
            console.error('Invalid date:', date);
            return '';
        }
        
        const now = new Date();
        const diffInSeconds = Math.floor((now - dateObj) / 1000);
        
        if (diffInSeconds < 60) {
            return 'Vừa xong';
        }
        
        const diffInMinutes = Math.floor(diffInSeconds / 60);
        
        if (diffInMinutes < 60) {
            return `${diffInMinutes} phút trước`;
        }
        
        const diffInHours = Math.floor(diffInMinutes / 60);
        
        if (diffInHours < 24) {
            return `${diffInHours} giờ trước`;
        }
        
        const diffInDays = Math.floor(diffInHours / 24);
        
        if (diffInDays < 30) {
            return `${diffInDays} ngày trước`;
        }
        
        const diffInMonths = Math.floor(diffInDays / 30);
        
        if (diffInMonths < 12) {
            return `${diffInMonths} tháng trước`;
        }
        
        const diffInYears = Math.floor(diffInMonths / 12);
        
        return `${diffInYears} năm trước`;
    }
};

// String Utilities
const StringUtils = {
    /**
     * Truncate text to specified length
     * @param {string} text - Text to truncate
     * @param {number} [length=100] - Maximum length
     * @param {string} [suffix='...'] - Suffix to add when truncated
     * @returns {string} - Truncated text
     */
    truncate: (text, length = 100, suffix = '...') => {
        if (!text || text.length <= length) return text;
        return text.substring(0, length).trim() + suffix;
    },

    /**
     * Slugify text for URLs
     * @param {string} text - Text to slugify
     * @returns {string} - Slugified text
     */
    slugify: (text) => {
        if (!text) return '';
        
        return text
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .replace(/[đ]/g, 'd')
            .replace(/[^a-z0-9 ]/g, '')
            .replace(/\s+/g, '-');
    },

    /**
     * Format currency
     * @param {number} amount - Amount to format
     * @param {string} [currency='VND'] - Currency code
     * @param {string} [locale='vi-VN'] - Locale
     * @returns {string} - Formatted currency
     */
    formatCurrency: (amount, currency = 'VND', locale = 'vi-VN') => {
        if (amount === null || amount === undefined) return '';
        
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency,
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }
};

// Form Utilities
const FormUtils = {
    /**
     * Serialize form to object
     * @param {Element|string} form - Form element or selector
     * @returns {Object} - Form data as object
     */
    serialize: (form) => {
        const formElement = typeof form === 'string' ? DOM.select(form) : form;
        
        if (!formElement || !(formElement instanceof HTMLFormElement)) {
            console.error('Invalid form element:', form);
            return {};
        }
        
        const formData = new FormData(formElement);
        const result = {};
        
        for (const [key, value] of formData.entries()) {
            if (result[key] !== undefined) {
                if (!Array.isArray(result[key])) {
                    result[key] = [result[key]];
                }
                result[key].push(value);
            } else {
                result[key] = value;
            }
        }
        
        return result;
    },

    /**
     * Reset form
     * @param {Element|string} form - Form element or selector
     */
    reset: (form) => {
        const formElement = typeof form === 'string' ? DOM.select(form) : form;
        
        if (!formElement || !(formElement instanceof HTMLFormElement)) {
            console.error('Invalid form element:', form);
            return;
        }
        
        formElement.reset();
        
        // Also reset any custom validation UI
        formElement.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        
        formElement.querySelectorAll('.invalid-feedback').forEach(el => {
            el.textContent = '';
        });
    }
};

// Export all utilities
const Utils = {
    DOM,
    Storage,
    URL,
    DateUtils,
    StringUtils,
    FormUtils
};

// Make available globally
window.Utils = Utils; 