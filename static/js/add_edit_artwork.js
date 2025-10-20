
$(document).ready(function() {
    // 图片URL预览
    $('#image_url').on('input', function() {
        const url = $(this).val();
        const preview = $('#imagePreview');

        if (url) {
            preview.attr('src', url).show();
        } else {
            preview.hide();
        }
    });

    // 初始预览（编辑模式）
    {% if artwork and artwork.image_url %}
        $('#imagePreview').attr('src', '{{ artwork.image_url }}').show();
    {% endif %}

    // 标签管理
    $('#tags').on('keypress', function(e) {
        if (e.which === 13 || e.which === 44) { // Enter or comma
            e.preventDefault();
            addTag($(this).val().trim());
            $(this).val('');
        }
    });

    function addTag(tagText) {
        if (!tagText) return;

        // 检查是否已存在
        if ($('#tagsContainer').find('.tag-badge:contains("' + tagText + '")').length > 0) {
            return;
        }

        const tagHtml = `
            <span class="tag-badge">
                ${tagText}
                <span class="remove-tag" data-tag="${tagText}">×</span>
            </span>
        `;

        $('#tagsContainer').append(tagHtml);
        updateTagsInput();
    }

    // 移除标签
    $(document).on('click', '.remove-tag', function() {
        $(this).closest('.tag-badge').remove();
        updateTagsInput();
    });

    function updateTagsInput() {
        const tags = [];
        $('#tagsContainer .tag-badge').each(function() {
            tags.push($(this).contents().filter(function() {
                return this.nodeType === 3; // Text node
            }).text().trim());
        });
        $('#tagsInput').val(tags.join(','));
    }



$('#process_images').on('input', function() {
    const rawText = $(this).val().trim();
    const urls = rawText.split(',') 
                        .map(item => item.split(/\s+/)) 
                        .flat() 
                        .map(url => url.trim()) 
                        .filter(url => url.length > 0); 

    const container = $('#processImagesPreview');
    container.empty();

    urls.forEach(url => {
        const trimmedUrl = url.trim();
        if (trimmedUrl) {
            const img = $('<img>', {
                class: 'process-image-preview',
                src: trimmedUrl,
                alt: 'Process image',
                onerror: "this.style.display='none'",
            });
            container.append(img);
        }
    });
});

    // 表单提交验证
    $('#artworkForm').on('submit', function(e) {
        const title = $('#title').val().trim();
        const imageUrl = $('#image_url').val().trim();
        const description = $('#description').val().trim();

        if (!title) {
            e.preventDefault();
            alert('Please enter a title for your artwork');
            $('#title').focus();
            return;
        }

        if (!imageUrl) {
            e.preventDefault();
            alert('Please provide an image URL for your artwork');
            $('#image_url').focus();
            return;
        }

        if(!description) {
            e.preventDefault();
            alert('Please enter a description for your artwork');
            $('#description').focus();
            return;
        }

        // 显示提交中状态
        const submitBtn = $(this).find('button[type="submit"]');
        submitBtn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Publishing...');
    });

    // 搜索框回车提交
    $('input[name="q"]').keypress(function(e) {
        if (e.which === 13) {
            $(this).closest('form').submit();
        }
    });

    // 初始化标签输入（编辑模式）
    {% if artwork and artwork.tags %}
        updateTagsInput();
    {% endif %}

    // 初始化过程图片预览（编辑模式）
    {% if artwork and artwork.process_images %}
        $('#process_images').trigger('input');
    {% endif %}
});
