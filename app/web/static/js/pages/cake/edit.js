/**
 * JavaScript for Edit Cake page
 * Handles form submission, validation, image upload and deletion
 */

jQuery(function($) {
    console.log('Cake edit.js loaded');
    
    // DEBUG - Log giá trị từ form ban đầu
    console.log('Form data debugging:');
    console.log('- Original source value:', $('#original_source').val());
    console.log('- Source select value:', $('#source').val());
    console.log('- Price-type rows count:', $('.price-type-row').length);
    console.log('- Price values:', $('input[name="prices[]"]').map(function() { return $(this).val(); }).get());
    console.log('- Form values:', $('input[name="form[]"]').map(function() { return $(this).val(); }).get());
    
    // Debug cake data structure
    console.log('priceTypeContainer HTML:');
    console.log($('#priceTypeContainer').html());
    
    // Xử lý trường source - Nâng cao để đảm bảo luôn chọn đúng nguồn
    const originalSource = $('#original_source').val();
    console.log('Original source from API:', originalSource);
    
    if (originalSource && originalSource.trim() !== '') {
        // Kiểm tra chính xác (case sensitive)
        let exactMatchFound = false;
        $('#source option').each(function() {
            if ($(this).val() === originalSource) {
                $(this).prop('selected', true);
                exactMatchFound = true;
                console.log('Found exact match source option:', $(this).val());
                return false; // break loop
            }
        });
        
        // Nếu không có exact match, kiểm tra case insensitive
        if (!exactMatchFound) {
            let caseInsensitiveFound = false;
            const originalSourceLower = originalSource.toLowerCase().trim();
            
            $('#source option').each(function() {
                const optionVal = $(this).val().toLowerCase().trim();
                console.log(`Comparing source option (case insensitive): "${optionVal}" with original: "${originalSourceLower}"`);
                
                if (optionVal && optionVal === originalSourceLower) {
                    $(this).prop('selected', true);
                    caseInsensitiveFound = true;
                    console.log('Found case insensitive match source option:', $(this).val());
                    return false; // break loop
                }
            });
            
            // Nếu không tìm thấy, thêm option mới
            if (!caseInsensitiveFound && originalSource.trim() !== '') {
                console.log('Adding custom source option:', originalSource);
                $('#source').append($('<option>', {
                    value: originalSource,
                    text: originalSource,
                    selected: true
                }));
            }
        }
        
        // Force source selection từ original nếu không có lựa chọn nào được chọn
        if (!$('#source').val() && originalSource) {
            console.log('Forcing source selection to:', originalSource);
            $('#source').append($('<option>', {
                value: originalSource,
                text: originalSource,
                selected: true
            }));
        }
        
        // Re-check nguồn sau khi xử lý
        console.log('Source select value after processing:', $('#source').val());
    }
    
    // Xử lý preview hình ảnh
    $('#file').change(function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                $('#imagePreview').html(`<img src="${e.target.result}" class="img-fluid" alt="Preview">`);
            }
            reader.readAsDataURL(file);
            $(this).next('.custom-file-label').html(file.name);
        }
    });

    // Xử lý thêm mới giá và loại bánh
    $('#addPriceType').click(function() {
        console.log('Adding new price and type row');
        const template = `
            <div class="price-type-row mb-3">
                <div class="row">
                    <div class="col-md-5">
                        <div class="input-group">
                            <input type="number" class="form-control" name="prices[]" min="0" step="1000" placeholder="Giá" required>
                            <div class="input-group-append">
                                <span class="input-group-text">VNĐ</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-5">
                        <input type="text" class="form-control" name="form[]" placeholder="Loại bánh" required>
                    </div>
                    <div class="col-md-2">
                        <button type="button" class="btn btn-danger btn-remove-price-type">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
        $('#priceTypeContainer').append(template);
    });

    // Xử lý xóa giá và loại bánh
    $(document).on('click', '.btn-remove-price-type', function() {
        if ($('.price-type-row').length > 1) {
            $(this).closest('.price-type-row').remove();
        } else {
            alert('Phải có ít nhất một giá và loại bánh!');
        }
    });

    // Xử lý submit form
    $('#editCakeForm').submit(function(e) {
        e.preventDefault();
        console.log('Form submission started');
        
        // Validate form
        if (!this.checkValidity()) {
            e.stopPropagation();
            $(this).addClass('was-validated');
            console.log('Form validation failed');
            return;
        }
        
        // Validate source selection
        if (!$('#source').val()) {
            alert('Vui lòng chọn nguồn bánh!');
            $('#source').focus();
            console.log('Source validation failed');
            return;
        }
        
        // Lấy cake ID từ form
        const cakeId = $(this).data('cake-id');
        if (!cakeId) {
            console.error('Không tìm thấy ID bánh');
            alert('Có lỗi xảy ra: Không tìm thấy ID bánh');
            return;
        }
        
        // Tạo FormData object
        const formData = new FormData();
        
        // Thêm các trường cơ bản
        formData.append('name', $('#name').val());
        formData.append('description', $('#description').val());
        formData.append('source', $('#source').val());
        
        // Thêm file nếu có
        const fileInput = $('#file')[0];
        if (fileInput.files.length > 0) {
            formData.append('file', fileInput.files[0]);
            console.log('Added file:', fileInput.files[0].name);
        } else {
            console.log('No new file selected, keeping existing image');
        }
        
        // Lấy tất cả giá trị price và form
        const prices = [];
        const forms = [];
        
        // Kiểm tra và thu thập giá trị price
        let priceValid = true;
        $('input[name="prices[]"]').each(function(index) {
            const priceVal = $(this).val();
            const price = parseFloat(priceVal);
            
            if (!priceVal || isNaN(price)) {
                alert(`Giá tại dòng ${index + 1} không hợp lệ. Vui lòng nhập số.`);
                $(this).focus();
                priceValid = false;
                return false; // break loop
            }
            
            prices.push(price);
        });
        
        // Nếu có giá không hợp lệ, dừng xử lý
        if (!priceValid) {
            console.log('Price validation failed');
            return;
        }
        
        // Kiểm tra và thu thập giá trị form
        let formValid = true;
        $('input[name="form[]"]').each(function(index) {
            const formValue = $(this).val().trim();
            
            if (!formValue) {
                alert(`Loại bánh tại dòng ${index + 1} không được để trống.`);
                $(this).focus();
                formValid = false;
                return false; // break loop
            }
            
            forms.push(formValue);
        });
        
        // Nếu có form không hợp lệ, dừng xử lý
        if (!formValid) {
            console.log('Form validation failed');
            return;
        }
        
        // Kiểm tra số lượng price và form phải bằng nhau
        if (prices.length !== forms.length) {
            console.error('Số lượng giá và loại bánh không khớp:', prices.length, forms.length);
            alert('Có lỗi xảy ra trong dữ liệu giá và loại bánh. Vui lòng kiểm tra lại.');
            return;
        }
        

        // Thêm mảng price và form
        prices.forEach(price => {
            formData.append('prices', price);
        });
        
        forms.forEach(form => {
            formData.append('form', form);
        });

        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.html();
        
        submitBtn.html('<i class="fas fa-spinner fa-spin"></i> Đang lưu...');
        submitBtn.prop('disabled', true);

        // Log FormData để debug
        console.log('Submitting form data:');
        for (let pair of formData.entries()) {
            console.log(pair[0] + ': ' + pair[1]);
        }
        
        // Gửi form data
        $.ajax({
            url: '/cake/edit/' + cakeId,
            type: 'PUT', // Sử dụng POST theo endpoint trong cake_route.py
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                console.log('Success:', response);
                alert('Cập nhật bánh thành công!');
                window.location.href = '/cake/web';
            },
            error: function(xhr, status, error) {
                console.error('Error:', {
                    status: xhr.status,
                    statusText: xhr.statusText,
                    responseText: xhr.responseText
                });
                
                let errorMessage = 'Có lỗi xảy ra';
                try {
                    const response = JSON.parse(xhr.responseText);
                    console.log('Parsed error response:', response);
                    errorMessage = response.detail?.message || response.message || errorMessage;
                } catch (e) {
                    console.error('Error parsing response:', e);
                }
                
                alert(errorMessage + '. Vui lòng thử lại');
                submitBtn.html(originalText);
                submitBtn.prop('disabled', false);
            }
        });
    });
}); 