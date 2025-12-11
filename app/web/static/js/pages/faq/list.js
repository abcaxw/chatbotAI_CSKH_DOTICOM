document.addEventListener('DOMContentLoaded', function() {
    // Xử lý hiển thị/ẩn câu trả lời FAQ
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const toggleBtn = item.querySelector('.toggle-btn');
        const faqContent = item.querySelector('.faq-content');
        
        if (toggleBtn && faqContent) {
            toggleBtn.addEventListener('click', function() {
                // Toggle active class cho nút
                this.classList.toggle('active');
                
                // Toggle hiển thị nội dung
                faqContent.classList.toggle('active');
            });
        }
    });

    // Xử lý lọc theo danh mục
    const filterBadges = document.querySelectorAll('.filter-badge');
    
    filterBadges.forEach(badge => {
        badge.addEventListener('click', function() {
            const categoryId = this.getAttribute('data-category');
            
            // Toggle active class cho badge
            this.classList.toggle('active');
            
            // Xác định các danh mục đang được chọn
            const activeCategories = Array.from(document.querySelectorAll('.filter-badge.active'))
                .map(b => b.getAttribute('data-category'));
            
            // Cập nhật URL với tham số lọc
            let url = new URL(window.location.href);
            let params = new URLSearchParams(url.search);
            
            if (activeCategories.length > 0) {
                params.set('categories', activeCategories.join(','));
            } else {
                params.delete('categories');
            }
            
            // Reset về trang 1
            params.set('page', '1');
            
            // Chuyển hướng đến URL mới
            window.location.href = `${url.pathname}?${params.toString()}`;
        });
    });

    // Xử lý chuyển đổi giữa chế độ xem danh sách và lưới
    const listViewBtn = document.getElementById('list-view-btn');
    const gridViewBtn = document.getElementById('grid-view-btn');
    const listView = document.getElementById('faq-accordion');
    const gridView = document.getElementById('faq-grid');

    if (listViewBtn && gridViewBtn && listView && gridView) {
        // Kiểm tra xem người dùng đã lưu chế độ xem nào trước đó
        const savedView = localStorage.getItem('faq-view-mode');
        if (savedView === 'grid') {
            showGridView();
        } else {
            showListView();
        }

        listViewBtn.addEventListener('click', showListView);
        gridViewBtn.addEventListener('click', showGridView);
    }

    function showListView() {
        listView.style.display = 'block';
        gridView.style.display = 'none';
        listViewBtn.classList.add('active');
        gridViewBtn.classList.remove('active');
        localStorage.setItem('faq-view-mode', 'list');
    }

    function showGridView() {
        listView.style.display = 'none';
        gridView.style.display = 'grid';
        listViewBtn.classList.remove('active');
        gridViewBtn.classList.add('active');
        localStorage.setItem('faq-view-mode', 'grid');
    }

    // Xử lý tìm kiếm
    const searchForm = document.querySelector('.search-box form');
    
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = this.querySelector('input[name="q"]');
            
            if (searchInput && searchInput.value.trim()) {
                // Lấy các tham số hiện tại
                let url = new URL(window.location.href);
                let params = new URLSearchParams(url.search);
                
                // Cập nhật tham số tìm kiếm
                params.set('q', searchInput.value.trim());
                params.set('page', '1');
                
                // Chuyển hướng đến URL mới
                window.location.href = `${url.pathname}?${params.toString()}`;
            }
        });
    }

    // Xử lý modal xác nhận xóa
    const deleteModal = document.getElementById('delete-modal');
    const deleteButtons = document.querySelectorAll('.delete-action');
    const confirmDeleteButton = document.getElementById('confirm-delete');
    const cancelDeleteButton = document.getElementById('cancel-delete');
    let faqIdToDelete = null;

    // Hiển thị modal khi nhấn nút xóa
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            faqIdToDelete = this.getAttribute('data-id');
            deleteModal.style.display = 'flex';
        });
    });

    // Đóng modal khi nhấn nút hủy
    if (cancelDeleteButton) {
        cancelDeleteButton.addEventListener('click', function() {
            deleteModal.style.display = 'none';
            faqIdToDelete = null;
        });
    }

    // Xóa FAQ khi nhấn nút xác nhận
    if (confirmDeleteButton) {
        confirmDeleteButton.addEventListener('click', function() {
            if (faqIdToDelete) {
                // Gọi API xóa FAQ
                fetch(`/faq/delete/${faqIdToDelete}`, {
                    method: 'DELETE',
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    }
                    throw new Error('Không thể xóa câu hỏi.');
                })
                .then(data => {
                    // Hiển thị thông báo thành công
                    showNotification('Xóa câu hỏi thành công!', 'success');
                    
                    // Tải lại trang sau khi xóa thành công
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                })
                .catch(error => {
                    showNotification(error.message, 'error');
                })
                .finally(() => {
                    deleteModal.style.display = 'none';
                    faqIdToDelete = null;
                });
            }
        });
    }

    // Đóng modal khi click bên ngoài
    window.addEventListener('click', function(e) {
        if (e.target === deleteModal) {
            deleteModal.style.display = 'none';
            faqIdToDelete = null;
        }
    });

    // Hàm hiển thị thông báo
    function showNotification(message, type) {
        // Sử dụng component notification.js nếu có
        if (typeof notification !== 'undefined' && notification.show) {
            notification.show(message, type);
            return;
        }
        
        // Kiểm tra xem đã có container thông báo chưa
        let notificationContainer = document.querySelector('.notification-container');
        
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.className = 'notification-container';
            document.body.appendChild(notificationContainer);
            
            // Thêm CSS cho container
            notificationContainer.style.position = 'fixed';
            notificationContainer.style.top = '20px';
            notificationContainer.style.right = '20px';
            notificationContainer.style.zIndex = '1000';
        }
        
        // Tạo thông báo mới
        const notificationElement = document.createElement('div');
        notificationElement.className = `notification ${type}`;
        notificationElement.textContent = message;
        
        // Thêm CSS cho thông báo
        notificationElement.style.backgroundColor = type === 'success' ? '#6bc253' : '#e74c3c';
        notificationElement.style.color = 'white';
        notificationElement.style.padding = '12px 20px';
        notificationElement.style.marginBottom = '10px';
        notificationElement.style.borderRadius = '4px';
        notificationElement.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.2)';
        notificationElement.style.transition = 'all 0.3s ease';
        
        // Thêm thông báo vào container
        notificationContainer.appendChild(notificationElement);
        
        // Tự động ẩn thông báo sau 3 giây
        setTimeout(() => {
            notificationElement.style.opacity = '0';
            setTimeout(() => {
                notificationContainer.removeChild(notificationElement);
            }, 300);
        }, 3000);
    }
}); 