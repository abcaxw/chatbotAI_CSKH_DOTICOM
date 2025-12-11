document.addEventListener('DOMContentLoaded', function() {
    // Xử lý chuyển đổi giữa chế độ xem danh sách và lưới
    const listViewBtn = document.getElementById('list-view-btn');
    const gridViewBtn = document.getElementById('grid-view-btn');
    const listView = document.getElementById('list-view');
    const gridView = document.getElementById('grid-view');

    if (listViewBtn && gridViewBtn) {
        // Kiểm tra xem người dùng đã lưu chế độ xem nào trước đó
        const savedView = localStorage.getItem('document-view-mode');
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
        localStorage.setItem('document-view-mode', 'list');
    }

    function showGridView() {
        listView.style.display = 'none';
        gridView.style.display = 'grid';
        listViewBtn.classList.remove('active');
        gridViewBtn.classList.add('active');
        localStorage.setItem('document-view-mode', 'grid');
    }

    // Xử lý lọc bánh
    const filterCategory = document.getElementById('filter-category');
    const filterDate = document.getElementById('filter-date');

    if (filterCategory) {
        filterCategory.addEventListener('change', applyFilters);
    }

    if (filterDate) {
        filterDate.addEventListener('change', applyFilters);
    }

    function applyFilters() {
        const categoryValue = filterCategory ? filterCategory.value : '';
        const dateValue = filterDate ? filterDate.value : '';
        
        // Tạo query string từ các giá trị filter
        let queryParams = new URLSearchParams(window.location.search);
        
        if (categoryValue) {
            queryParams.set('category', categoryValue);
        } else {
            queryParams.delete('category');
        }
        
        if (dateValue) {
            queryParams.set('date', dateValue);
        } else {
            queryParams.delete('date');
        }
        
        // Giữ nguyên tham số tìm kiếm
        const searchValue = queryParams.get('q');
        if (searchValue) {
            queryParams.set('q', searchValue);
        }
        
        // Reset về trang 1 khi lọc
        queryParams.set('page', '1');
        
        // Chuyển hướng đến URL với query params mới
        window.location.href = window.location.pathname + '?' + queryParams.toString();
    }

    // Xử lý modal xác nhận xóa
    const deleteModal = document.getElementById('delete-modal');
    const deleteButtons = document.querySelectorAll('.delete-action');
    const confirmDeleteButton = document.getElementById('confirm-delete');
    const cancelDeleteButton = document.getElementById('cancel-delete');
    let documentIdToDelete = null;

    // Hiển thị modal khi nhấn nút xóa
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            documentIdToDelete = this.getAttribute('data-id');
            deleteModal.style.display = 'flex';
        });
    });

    // Đóng modal khi nhấn nút hủy
    if (cancelDeleteButton) {
        cancelDeleteButton.addEventListener('click', function() {
            deleteModal.style.display = 'none';
            documentIdToDelete = null;
        });
    }

    // Xóa document khi nhấn nút xác nhận
    if (confirmDeleteButton) {
        confirmDeleteButton.addEventListener('click', function() {
            if (documentIdToDelete) {
                // Gọi API xóa document
                fetch(`/document/delete/${documentIdToDelete}`, {
                    method: 'DELETE',
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    }
                    throw new Error('Không thể xóa tài liệu.');
                })
                .then(data => {
                    // Hiển thị thông báo thành công
                    showNotification('Xóa tài liệu thành công!', 'success');
                    
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
                    documentIdToDelete = null;
                });
            }
        });
    }

    // Đóng modal khi click bên ngoài
    window.addEventListener('click', function(e) {
        if (e.target === deleteModal) {
            deleteModal.style.display = 'none';
            documentIdToDelete = null;
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