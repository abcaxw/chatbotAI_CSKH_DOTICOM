document.addEventListener("DOMContentLoaded", function () {
  // Xử lý chuyển đổi giữa chế độ xem danh sách và lưới
  const listViewBtn = document.getElementById("list-view-btn");
  const gridViewBtn = document.getElementById("grid-view-btn");
  const listView = document.getElementById("list-view");
  const gridView = document.getElementById("grid-view");

  if (listViewBtn && gridViewBtn) {
    // Kiểm tra xem người dùng đã lưu chế độ xem nào trước đó
    const savedView = localStorage.getItem("cake-view-mode");
    if (savedView === "list") {
      showListView();
    } else {
      showGridView();
    }

    listViewBtn.addEventListener("click", showListView);
    gridViewBtn.addEventListener("click", showGridView);
  }

  function showListView() {
    listView.style.display = "block";
    gridView.style.display = "none";
    listViewBtn.classList.add("active");
    gridViewBtn.classList.remove("active");
    localStorage.setItem("cake-view-mode", "list");
  }

  function showGridView() {
    listView.style.display = "none";
    gridView.style.display = "grid";
    listViewBtn.classList.remove("active");
    gridViewBtn.classList.add("active");
    localStorage.setItem("cake-view-mode", "grid");
  }

  // Xử lý lọc bánh
  const filterCategory = document.getElementById("filter-category");
  const filterPrice = document.getElementById("filter-price");
  const filterSource = document.getElementById("filter-source");

  if (filterCategory) {
    filterCategory.addEventListener("change", applyFilters);
  }

  if (filterPrice) {
    filterPrice.addEventListener("change", applyFilters);
  }
  
  if (filterSource) {
    filterSource.addEventListener("change", applyFilters);
  }

  function applyFilters() {
    const categoryValue = filterCategory ? filterCategory.value : "";
    const priceValue = filterPrice ? filterPrice.value : "";
    const sourceValue = filterSource ? filterSource.value : "";

    // Tạo query string từ các giá trị filter
    let queryParams = new URLSearchParams(window.location.search);

    if (categoryValue) {
      queryParams.set("category", categoryValue);
    } else {
      queryParams.delete("category");
    }

    if (priceValue) {
      queryParams.set("price", priceValue);
    } else {
      queryParams.delete("price");
    }
    
    if (sourceValue) {
      queryParams.set("source", sourceValue);
    } else {
      queryParams.delete("source");
    }

    // Giữ nguyên tham số tìm kiếm
    const searchValue = queryParams.get("q");
    if (searchValue) {
      queryParams.set("q", searchValue);
    }

    // Reset về trang 1 khi lọc
    queryParams.set("page", "1");

    // Chuyển hướng đến URL với query params mới
    window.location.href =
      window.location.pathname + "?" + queryParams.toString();
  }

  // Xử lý modal xác nhận xóa
  const deleteModal = document.getElementById("delete-modal");
  const deleteButtons = document.querySelectorAll(".delete-action");
  const confirmDeleteButton = document.getElementById("confirm-delete");
  const cancelDeleteButton = document.getElementById("cancel-delete");
  let cakeIdToDelete = null;

  // Hiển thị modal khi nhấn nút xóa
  deleteButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      cakeIdToDelete = this.getAttribute("data-id");
      deleteModal.style.display = "flex";
    });
  });

  // Đóng modal khi nhấn nút hủy
  if (cancelDeleteButton) {
    cancelDeleteButton.addEventListener("click", function () {
      deleteModal.style.display = "none";
      cakeIdToDelete = null;
    });
  }

  // Xóa cake khi nhấn nút xác nhận
  if (confirmDeleteButton) {
    confirmDeleteButton.addEventListener("click", function () {
      if (cakeIdToDelete) {
        // Gọi API xóa cake
        fetch(`/cake/delete/${cakeIdToDelete}`, {
          method: "DELETE",
        })
          .then((response) => {
            if (response.ok) {
              return response.json();
            }
            throw new Error("Không thể xóa bánh.");
          })
          .then((data) => {
            // Hiển thị thông báo thành công
            showNotification("Xóa bánh thành công!", "success");

            // Tải lại trang sau khi xóa thành công
            setTimeout(() => {
              window.location.reload();
            }, 1000);
          })
          .catch((error) => {
            showNotification(error.message, "error");
          })
          .finally(() => {
            deleteModal.style.display = "none";
            cakeIdToDelete = null;
          });
      }
    });
  }

  // Đóng modal khi click bên ngoài
  window.addEventListener("click", function (e) {
    if (e.target === deleteModal) {
      deleteModal.style.display = "none";
      cakeIdToDelete = null;
    }
  });

  // Xử lý chức năng xem trước ảnh bánh
  const cakeImages = document.querySelectorAll(".cake-image");
  const previewModal = document.getElementById("image-preview-modal");
  const previewImage = document.getElementById("preview-image");
  const closePreviewButton = document.getElementById("close-preview");

  // Hiển thị modal xem trước khi click vào ảnh bánh
  if (cakeImages && previewModal && previewImage) {
    cakeImages.forEach((img) => {
      img.addEventListener("click", function () {
        const imgSrc = this.getAttribute("src");
        previewImage.setAttribute("src", imgSrc);
        previewModal.style.display = "flex";
      });
    });

    // Đóng modal xem trước
    if (closePreviewButton) {
      closePreviewButton.addEventListener("click", function () {
        previewModal.style.display = "none";
      });
    }

    // Đóng modal khi click bên ngoài
    window.addEventListener("click", function (e) {
      if (e.target === previewModal) {
        previewModal.style.display = "none";
      }
    });
  }

  // Hàm hiển thị thông báo
  function showNotification(message, type) {
    // Sử dụng component notification.js nếu có
    if (typeof notification !== "undefined" && notification.show) {
      notification.show(message, type);
      return;
    }

    // Kiểm tra xem đã có container thông báo chưa
    let notificationContainer = document.querySelector(
      ".notification-container"
    );

    if (!notificationContainer) {
      notificationContainer = document.createElement("div");
      notificationContainer.className = "notification-container";
      document.body.appendChild(notificationContainer);

      // Thêm CSS cho container
      notificationContainer.style.position = "fixed";
      notificationContainer.style.top = "20px";
      notificationContainer.style.right = "20px";
      notificationContainer.style.zIndex = "1000";
    }

    // Tạo thông báo mới
    const notificationElement = document.createElement("div");
    notificationElement.className = `notification ${type}`;
    notificationElement.textContent = message;

    // Thêm CSS cho thông báo
    notificationElement.style.backgroundColor =
      type === "success" ? "#6bc253" : "#e74c3c";
    notificationElement.style.color = "white";
    notificationElement.style.padding = "12px 20px";
    notificationElement.style.marginBottom = "10px";
    notificationElement.style.borderRadius = "4px";
    notificationElement.style.boxShadow = "0 2px 5px rgba(0, 0, 0, 0.2)";
    notificationElement.style.transition = "all 0.3s ease";

    // Thêm thông báo vào container
    notificationContainer.appendChild(notificationElement);

    // Tự động ẩn thông báo sau 3 giây
    setTimeout(() => {
      notificationElement.style.opacity = "0";
      setTimeout(() => {
        notificationContainer.removeChild(notificationElement);
      }, 300);
    }, 3000);
  }
});
