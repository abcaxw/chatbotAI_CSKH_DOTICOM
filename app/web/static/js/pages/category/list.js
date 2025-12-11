document.addEventListener('DOMContentLoaded', function() {
    // Fetch và hiển thị danh sách danh mục ngay khi trang được tải
    fetchCategories();

    async function fetchCategories() {
        try {
            // Lấy thông tin trang và query từ URL
            const urlParams = new URLSearchParams(window.location.search);
            const page = urlParams.get('page') || 1;
            const query = urlParams.get('q') || '';
            const type = urlParams.get('type') || '';
            
            // Chuẩn bị dữ liệu phân trang
            const paginationData = {
                page: parseInt(page),
                limit: 10,
                search: query,
                filter: type ? { type: type } : {}
            };
            
            // Gọi API để lấy danh sách danh mục
            const response = await fetch('/category/get-categories-by-pagination', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(paginationData)
            });
            
            if (!response.ok) {
                throw new Error('Không thể tải danh mục');
            }
            
            const result = await response.json();
            
            // Render danh mục vào listView và gridView
            if (result.data && result.data.categories) {
                renderCategories(result.data.categories);
            } else {
                showNotification('Không có danh mục nào', 'error');
            }
        } catch (error) {
            console.error('Lỗi khi tải danh mục:', error);
            showNotification('Không thể tải danh mục', 'error');
        }
    }
    
    function renderCategories(categories) {
        const listView = document.getElementById('list-view');
        const gridView = document.getElementById('grid-view');
        
        if (!listView || !gridView) {
            console.error('Không tìm thấy phần tử hiển thị danh mục');
            return;
        }
        
        // Xóa danh sách hiện tại
        listView.innerHTML = '';
        gridView.innerHTML = '';
        
        if (categories.length === 0) {
            listView.innerHTML = '<div class="empty-state">Không có danh mục nào</div>';
            gridView.innerHTML = '<div class="empty-state">Không có danh mục nào</div>';
            return;
        }
        
        // Render danh mục trong chế độ danh sách
        categories.forEach(category => {
            // Tạo phần tử danh sách
            const listItem = document.createElement('div');
            listItem.className = 'category-list-item';
            listItem.innerHTML = `
                <div class="category-list-icon">
                    <i class="fas ${getCategoryIcon(category.type)}"></i>
                </div>
                <div class="category-list-info">
                    <h3 class="category-list-name">${category.name}</h3>
                    <div class="category-list-meta">
                        <span class="category-list-type">
                            Loại: ${getCategoryTypeName(category.type)}
                        </span>
                        <span class="category-list-count">${category.item_count || 0} mục</span>
                    </div>
                </div>
                <div class="category-list-actions">
                    <a href="/category/edit/${category.id}" class="edit-action" title="Sửa"><i class="fas fa-edit"></i></a>
                    <button class="delete-action" data-id="${category.id}" data-usage="${category.item_count || 0}" title="Xóa"><i class="fas fa-trash"></i></button>
                </div>
            `;
            listView.appendChild(listItem);
            
            // Tạo phần tử lưới
            const gridItem = document.createElement('div');
            gridItem.className = 'category-card';
            gridItem.innerHTML = `
                <div class="category-icon">
                    <i class="fas ${getCategoryIcon(category.type)}"></i>
                </div>
                <div class="category-info">
                    <h3 class="category-name">${category.name}</h3>
                    <div class="category-type">
                        <i class="fas fa-tag"></i>
                        ${getCategoryTypeName(category.type)}
                    </div>
                    <span class="category-count">${category.item_count || 0} mục</span>
                </div>
                <div class="category-actions">
                    <a href="/category/edit/${category.id}" class="edit-action" title="Sửa"><i class="fas fa-edit"></i></a>
                    <button class="delete-action" data-id="${category.id}" data-usage="${category.item_count || 0}" title="Xóa"><i class="fas fa-trash"></i></button>
                </div>
            `;
            gridView.appendChild(gridItem);
        });
        
        // Gắn event listeners cho các nút xóa
        const deleteButtons = document.querySelectorAll('.delete-action');
        const deleteModal = document.getElementById('delete-modal');
        const confirmDeleteButton = document.getElementById('confirm-delete');
        const cancelDeleteButton = document.getElementById('cancel-delete');
        let categoryIdToDelete = null;

        // Xử lý sự kiện click nút xóa
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                categoryIdToDelete = this.getAttribute('data-id');
                const usageCount = parseInt(this.getAttribute('data-usage') || '0');
                const modalMessage = document.getElementById('delete-modal-message');
                
                if (modalMessage) {
                    modalMessage.textContent = usageCount > 0 
                        ? `Danh mục này đang được sử dụng bởi ${usageCount} mục. Bạn có chắc chắn muốn xóa?`
                        : 'Bạn có chắc chắn muốn xóa danh mục này?';
                }
                
                deleteModal.style.display = 'flex';
            });
        });

        // Xử lý sự kiện đóng modal
        if (cancelDeleteButton) {
            cancelDeleteButton.addEventListener('click', function() {
                deleteModal.style.display = 'none';
                categoryIdToDelete = null;
            });
        }

        // Xử lý sự kiện xác nhận xóa
        if (confirmDeleteButton) {
            confirmDeleteButton.addEventListener('click', async function() {
                if (categoryIdToDelete) {
                    try {
                        const response = await fetch(`/category/delete/${categoryIdToDelete}`, {
                            method: 'DELETE'
                        });

                        if (!response.ok) {
                            throw new Error('Không thể xóa danh mục.');
                        }

                        showNotification('Xóa danh mục thành công!', 'success');
                        fetchCategories(); // Tải lại danh sách
                    } catch (error) {
                        showNotification(error.message, 'error');
                    } finally {
                        deleteModal.style.display = 'none';
                        categoryIdToDelete = null;
                    }
                }
            });
        }

        // Đóng modal khi click ngoài
        window.addEventListener('click', function(e) {
            if (e.target === deleteModal) {
                deleteModal.style.display = 'none';
                categoryIdToDelete = null;
            }
        });
    }
    
    function getCategoryIcon(type) {
        switch(type) {
            case 'cake': return 'fa-birthday-cake';
            case 'document': return 'fa-file-alt';
            case 'faq': return 'fa-question-circle';
            default: return 'fa-folder';
        }
    }
    
    function getCategoryTypeName(type) {
        switch(type) {
            case 'cake': return 'Bánh';
            case 'document': return 'Tài liệu';
            case 'faq': return 'FAQ';
            default: return 'Khác';
        }
    }
    
    // Xử lý chuyển đổi giữa chế độ xem danh sách và lưới
    const listViewBtn = document.getElementById('list-view-btn');
    const gridViewBtn = document.getElementById('grid-view-btn');
    const listView = document.getElementById('list-view');
    const gridView = document.getElementById('grid-view');

    if (listViewBtn && gridViewBtn) {
        // Kiểm tra xem người dùng đã lưu chế độ xem nào trước đó
        const savedView = localStorage.getItem('category-view-mode');
        if (savedView === 'list') {
            showListView();
        } else {
            showGridView();
        }

        listViewBtn.addEventListener('click', showListView);
        gridViewBtn.addEventListener('click', showGridView);
    }

    function showListView() {
        listView.style.display = 'block';
        gridView.style.display = 'none';
        listViewBtn.classList.add('active');
        gridViewBtn.classList.remove('active');
        localStorage.setItem('category-view-mode', 'list');
    }

    function showGridView() {
        listView.style.display = 'none';
        gridView.style.display = 'grid';
        listViewBtn.classList.remove('active');
        gridViewBtn.classList.add('active');
        localStorage.setItem('category-view-mode', 'grid');
    }

    // Xử lý lọc danh mục
    const filterType = document.getElementById('filter-type');

    if (filterType) {
        filterType.addEventListener('change', function() {
            const typeValue = this.value;
            
            // Tạo query string từ giá trị filter
            let queryParams = new URLSearchParams(window.location.search);
            
            if (typeValue) {
                queryParams.set('type', typeValue);
            } else {
                queryParams.delete('type');
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
        });
    }

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