/**
 * Modal Component
 * Hiển thị cửa sổ modal với các tùy chọn tùy chỉnh
 */

class ModalManager {
    constructor() {
        this.modals = new Map();
        this.activeModal = null;
        this.zIndex = 1000;
    }

    /**
     * Tạo modal mới
     * @param {string} id - ID của modal
     * @param {Object} options - Các tùy chọn của modal
     * @returns {Object} Modal object
     */
    create(id, options = {}) {
        if (this.modals.has(id)) {
            console.warn(`Modal với ID ${id} đã tồn tại. Trả về modal đã tồn tại.`);
            return this.modals.get(id);
        }

        // Tạo container cho modal
        const modalContainer = document.createElement('div');
        modalContainer.className = 'modal';
        modalContainer.id = id;
        modalContainer.style.display = 'none';
        modalContainer.style.position = 'fixed';
        modalContainer.style.top = '0';
        modalContainer.style.left = '0';
        modalContainer.style.width = '100%';
        modalContainer.style.height = '100%';
        modalContainer.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        modalContainer.style.justifyContent = 'center';
        modalContainer.style.alignItems = 'center';
        modalContainer.style.zIndex = this.zIndex.toString();

        // Tạo nội dung modal
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        modalContent.style.backgroundColor = 'white';
        modalContent.style.borderRadius = '8px';
        modalContent.style.width = options.width || '90%';
        modalContent.style.maxWidth = options.maxWidth || '500px';
        modalContent.style.padding = options.padding || '2rem';
        modalContent.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.2)';
        modalContent.style.position = 'relative';

        // Thêm nút đóng nếu cần
        if (options.showCloseButton !== false) {
            const closeButton = document.createElement('button');
            closeButton.innerHTML = '&times;';
            closeButton.style.position = 'absolute';
            closeButton.style.top = '10px';
            closeButton.style.right = '15px';
            closeButton.style.border = 'none';
            closeButton.style.background = 'none';
            closeButton.style.fontSize = '1.5rem';
            closeButton.style.cursor = 'pointer';
            closeButton.style.color = '#666';
            closeButton.addEventListener('click', () => this.close(id));
            modalContent.appendChild(closeButton);
        }

        // Thêm tiêu đề nếu có
        if (options.title) {
            const title = document.createElement('h3');
            title.textContent = options.title;
            title.style.marginTop = '0';
            title.style.marginBottom = '1rem';
            modalContent.appendChild(title);
        }

        // Thêm nội dung
        if (options.content) {
            if (typeof options.content === 'string') {
                const content = document.createElement('div');
                content.innerHTML = options.content;
                modalContent.appendChild(content);
            } else if (options.content instanceof HTMLElement) {
                modalContent.appendChild(options.content);
            }
        }

        // Thêm các nút hành động nếu có
        if (options.actions && options.actions.length > 0) {
            const actionsContainer = document.createElement('div');
            actionsContainer.className = 'modal-actions';
            actionsContainer.style.display = 'flex';
            actionsContainer.style.justifyContent = 'flex-end';
            actionsContainer.style.marginTop = '2rem';
            actionsContainer.style.gap = '1rem';

            options.actions.forEach(action => {
                const button = document.createElement('button');
                button.textContent = action.text;
                button.className = action.className || '';
                
                // Thêm CSS cho button
                button.style.padding = '0.7rem 1.5rem';
                button.style.borderRadius = '4px';
                button.style.cursor = 'pointer';
                button.style.fontWeight = '500';
                button.style.border = 'none';
                button.style.transition = 'background-color 0.3s';
                
                if (action.primary) {
                    button.style.backgroundColor = '#ff6b6b';
                    button.style.color = 'white';
                } else {
                    button.style.backgroundColor = '#f8f9fa';
                    button.style.color = '#343a40';
                }
                
                button.addEventListener('click', () => {
                    if (action.callback) {
                        action.callback();
                    }
                    if (action.closeOnClick !== false) {
                        this.close(id);
                    }
                });
                
                actionsContainer.appendChild(button);
            });

            modalContent.appendChild(actionsContainer);
        }

        // Thêm modal vào DOM
        modalContainer.appendChild(modalContent);
        document.body.appendChild(modalContainer);

        // Lưu modal vào danh sách
        const modal = {
            id,
            element: modalContainer,
            content: modalContent,
            options
        };
        
        this.modals.set(id, modal);

        // Thêm sự kiện click bên ngoài để đóng modal
        if (options.closeOnOutsideClick !== false) {
            modalContainer.addEventListener('click', (e) => {
                if (e.target === modalContainer) {
                    this.close(id);
                }
            });
        }

        // Tăng zIndex cho modal tiếp theo
        this.zIndex += 10;

        return modal;
    }

    /**
     * Hiển thị modal
     * @param {string} id - ID của modal
     * @param {Object} options - Các tùy chọn bổ sung khi hiển thị
     */
    open(id, options = {}) {
        let modal = this.modals.get(id);
        
        // Nếu modal chưa tồn tại, tạo mới
        if (!modal) {
            modal = this.create(id, options);
        } else if (options) {
            // Cập nhật các tùy chọn nếu có
            if (options.title) {
                const titleElement = modal.content.querySelector('h3');
                if (titleElement) {
                    titleElement.textContent = options.title;
                }
            }
            if (options.content) {
                // Xóa nội dung cũ
                const children = Array.from(modal.content.children);
                children.forEach(child => {
                    if (!child.matches('h3, .modal-actions') && !child.style.position) {
                        modal.content.removeChild(child);
                    }
                });
                
                // Thêm nội dung mới
                if (typeof options.content === 'string') {
                    const content = document.createElement('div');
                    content.innerHTML = options.content;
                    modal.content.insertBefore(content, modal.content.querySelector('.modal-actions'));
                } else if (options.content instanceof HTMLElement) {
                    modal.content.insertBefore(options.content, modal.content.querySelector('.modal-actions'));
                }
            }
        }

        // Hiển thị modal
        modal.element.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Ngăn cuộn trang khi modal hiển thị
        
        this.activeModal = modal;
        
        // Thêm hiệu ứng
        modal.content.style.opacity = '0';
        modal.content.style.transform = 'translateY(-20px)';
        modal.content.style.transition = 'opacity 0.3s, transform 0.3s';
        
        setTimeout(() => {
            modal.content.style.opacity = '1';
            modal.content.style.transform = 'translateY(0)';
        }, 10);
        
        // Callback onOpen nếu có
        if (modal.options.onOpen) {
            modal.options.onOpen();
        }
        
        return modal;
    }

    /**
     * Đóng modal
     * @param {string} id - ID của modal
     */
    close(id) {
        const modal = this.modals.get(id);
        if (!modal) return;
        
        // Hiệu ứng đóng
        modal.content.style.opacity = '0';
        modal.content.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            modal.element.style.display = 'none';
            
            // Chỉ cho phép cuộn trang khi không còn modal nào hiển thị
            const anyVisibleModal = Array.from(this.modals.values()).some(m => 
                m.element.style.display === 'flex' && m.id !== id
            );
            
            if (!anyVisibleModal) {
                document.body.style.overflow = '';
            }
            
            // Callback onClose nếu có
            if (modal.options.onClose) {
                modal.options.onClose();
            }
        }, 300);
        
        this.activeModal = null;
    }

    /**
     * Xóa modal
     * @param {string} id - ID của modal
     */
    destroy(id) {
        const modal = this.modals.get(id);
        if (!modal) return;
        
        // Xóa khỏi DOM
        document.body.removeChild(modal.element);
        
        // Xóa khỏi danh sách
        this.modals.delete(id);
        
        // Nếu đang là modal active, set active là null
        if (this.activeModal && this.activeModal.id === id) {
            this.activeModal = null;
        }
    }

    /**
     * Tạo modal xác nhận nhanh
     * @param {Object} options - Các tùy chọn của modal
     */
    confirm(options = {}) {
        const id = 'confirm-modal-' + Date.now();
        
        const modal = this.create(id, {
            title: options.title || 'Xác nhận',
            content: options.message || 'Bạn có chắc chắn muốn thực hiện hành động này?',
            actions: [
                {
                    text: options.confirmText || 'Xác nhận',
                    primary: true,
                    callback: options.onConfirm || (() => {})
                },
                {
                    text: options.cancelText || 'Hủy',
                    callback: options.onCancel || (() => {})
                }
            ],
            onClose: () => {
                // Tự động xóa modal confirm sau khi đóng
                setTimeout(() => this.destroy(id), 300);
            }
        });
        
        this.open(id);
        return modal;
    }

    /**
     * Tạo modal thông báo nhanh
     * @param {Object} options - Các tùy chọn của modal
     */
    alert(options = {}) {
        const id = 'alert-modal-' + Date.now();
        
        const modal = this.create(id, {
            title: options.title || 'Thông báo',
            content: options.message || '',
            actions: [
                {
                    text: options.okText || 'OK',
                    primary: true,
                    callback: options.onOk || (() => {})
                }
            ],
            onClose: () => {
                // Tự động xóa modal alert sau khi đóng
                setTimeout(() => this.destroy(id), 300);
            }
        });
        
        this.open(id);
        return modal;
    }
}

// Tạo instance singleton để sử dụng trong toàn bộ ứng dụng
const modal = new ModalManager();

// Export để sử dụng trong các module khác
if (typeof module !== 'undefined' && module.exports) {
    module.exports = modal;
} 