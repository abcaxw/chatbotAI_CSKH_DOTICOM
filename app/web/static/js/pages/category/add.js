document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('addCategoryForm');

    // Kiểm tra xem form có tồn tại không
    if (!form) {
        console.error('Form not found!');
        return; // Dừng thực thi nếu không tìm thấy form
    }

    // Xử lý submit form
    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const name = document.getElementById('name').value;
        const status = document.getElementById('status').value;

        try {
            const response = await fetch('/category/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, status }) // Gửi tên và trạng thái
            });

            if (response.ok) {
                alert('Thêm danh mục thành công');
                window.location.href = '/category/web'; // Quay lại trang danh sách
            } else {
                alert('Có lỗi xảy ra khi thêm danh mục');
            }
        } catch (error) {
            console.error('Lỗi khi thêm danh mục:', error);
            alert('Có lỗi xảy ra, vui lòng thử lại.');
        }
    });
});