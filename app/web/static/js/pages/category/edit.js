/**
 * JavaScript for Edit Category page
 * Handles form submission, validation, and image upload
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('editCategoryForm');
    const categoryId = document.getElementById('categoryId').value;

    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const name = document.getElementById('name').value;
            const status = document.getElementById('status').value;

            try {
                const response = await fetch(`/category/update-category/${categoryId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        name: name,
                        status: status
                    })
                });

                if (response.ok) {
                    showNotification('Cập nhật danh mục thành công!', 'success');
                    setTimeout(() => {
                        window.location.href = '/category/web';
                    }, 1000);
                } else {
                    const error = await response.json();
                    throw new Error(error.message || 'Có lỗi xảy ra');
                }
            } catch (error) {
                showNotification(error.message, 'error');
            }
        });
    }

    function showNotification(message, type) {
        let notificationContainer = document.querySelector('.notification-container');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.className = 'notification-container';
            notificationContainer.style.position = 'fixed';
            notificationContainer.style.top = '20px';
            notificationContainer.style.right = '20px';
            notificationContainer.style.zIndex = '1000';
            document.body.appendChild(notificationContainer);
        }
        
        const notificationElement = document.createElement('div');
        notificationElement.className = `notification ${type}`;
        notificationElement.textContent = message;
        
        notificationElement.style.backgroundColor = type === 'success' ? '#4caf50' : '#f44336';
        notificationElement.style.color = 'white';
        notificationElement.style.padding = '12px 24px';
        notificationElement.style.margin = '8px';
        notificationElement.style.borderRadius = '4px';
        notificationElement.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
        
        notificationContainer.appendChild(notificationElement);
        
        setTimeout(() => {
            notificationElement.remove();
        }, 3000);
    }
}); 