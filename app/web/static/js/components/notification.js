/**
 * Toast Notification Component
 * Hiển thị thông báo dạng toast với các loại: success, error, warning, info
 */

class NotificationManager {
    constructor() {
        this.container = null;
        this.init();
    }

    /**
     * Khởi tạo container chứa thông báo
     */
    init() {
        // Tạo container nếu chưa tồn tại
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'notification-container';
            
            // Thêm CSS cho container
            this.container.style.position = 'fixed';
            this.container.style.top = '20px';
            this.container.style.right = '20px';
            this.container.style.zIndex = '1000';
            
            document.body.appendChild(this.container);
        }
    }

    /**
     * Hiển thị thông báo
     * @param {string} message - Nội dung thông báo
     * @param {string} type - Loại thông báo: success, error, warning, info
     * @param {number} duration - Thời gian hiển thị tính bằng ms (mặc định 3000ms)
     */
    show(message, type = 'info', duration = 3000) {
        // Tạo thông báo mới
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Thêm CSS cho thông báo
        notification.style.backgroundColor = this.getColor(type);
        notification.style.color = 'white';
        notification.style.padding = '12px 20px';
        notification.style.marginBottom = '10px';
        notification.style.borderRadius = '4px';
        notification.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.2)';
        notification.style.transition = 'all 0.3s ease';
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(20px)';
        
        // Thêm thông báo vào container
        this.container.appendChild(notification);
        
        // Hiệu ứng hiển thị
        setTimeout(() => {
            notification.style.opacity = '1';
            notification.style.transform = 'translateX(0)';
        }, 10);
        
        // Tự động ẩn thông báo sau thời gian duration
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(20px)';
            
            // Xóa thông báo khỏi DOM sau khi kết thúc hiệu ứng
            setTimeout(() => {
                this.container.removeChild(notification);
            }, 300);
        }, duration);
    }

    /**
     * Lấy màu tương ứng với loại thông báo
     * @param {string} type - Loại thông báo
     * @returns {string} Mã màu dạng HEX
     */
    getColor(type) {
        switch (type) {
            case 'success':
                return '#6bc253';
            case 'error':
                return '#e74c3c';
            case 'warning':
                return '#f39c12';
            case 'info':
            default:
                return '#3498db';
        }
    }

    /**
     * Hiển thị thông báo thành công
     * @param {string} message - Nội dung thông báo
     * @param {number} duration - Thời gian hiển thị
     */
    success(message, duration) {
        this.show(message, 'success', duration);
    }

    /**
     * Hiển thị thông báo lỗi
     * @param {string} message - Nội dung thông báo
     * @param {number} duration - Thời gian hiển thị
     */
    error(message, duration) {
        this.show(message, 'error', duration);
    }

    /**
     * Hiển thị thông báo cảnh báo
     * @param {string} message - Nội dung thông báo
     * @param {number} duration - Thời gian hiển thị
     */
    warning(message, duration) {
        this.show(message, 'warning', duration);
    }

    /**
     * Hiển thị thông báo thông tin
     * @param {string} message - Nội dung thông báo
     * @param {number} duration - Thời gian hiển thị
     */
    info(message, duration) {
        this.show(message, 'info', duration);
    }
}

// Tạo instance singleton để sử dụng trong toàn bộ ứng dụng
const notification = new NotificationManager();

// Export để sử dụng trong các module khác
if (typeof module !== 'undefined' && module.exports) {
    module.exports = notification;
} 