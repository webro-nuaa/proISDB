// proISDB 主JavaScript文件

$(document).ready(function() {
    // 防止Bootstrap dropdown在初始化时闪烁
    $('.dropdown-menu').removeClass('show');
    
    // 初始化所有功能
    initializeModernNavbar();
    initializeBackToTop();
    initializeSearchSuggestions();
    initializeFileUpload();
    initializeFormValidation();
    initializeTooltips();
    initializeDataTables();
    initializeMobileMenu();
    
    // 防止dropdown意外展开
    preventDropdownFlicker();
});

// 现代化导航栏功能
function initializeModernNavbar() {
    // 导航栏滚动效果
    $(window).scroll(throttle(function() {
        // 如果正在通过TOC点击滚动，不改变导航栏状态
        if (window.disableNavbarScroll) return;
        
        if ($(window).scrollTop() > 50) {
            $('.modern-navbar').addClass('scrolled');
        } else {
            $('.modern-navbar').removeClass('scrolled');
        }
    }, 100));
    
    // 移动端汉堡菜单动画
    $('.modern-toggler').click(function() {
        $(this).toggleClass('active');
        
        // 添加点击波纹效果
        const ripple = $('<span class="toggler-ripple"></span>');
        $(this).append(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });
    
    // 导航项点击波纹效果
    $('.modern-nav-link').click(function(e) {
        const link = $(this);
        const ripple = $('<span class="nav-ripple"></span>');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        // 确保波纹不会影响布局
        ripple.css({
            position: 'absolute',
            width: size,
            height: size,
            left: x,
            top: y,
            pointerEvents: 'none',
            zIndex: 1
        });
        
        link.append(ripple);
        
        // 优化移除时机，防止抖动
        setTimeout(() => {
            ripple.fadeOut(200, function() {
                $(this).remove();
            });
        }, 400);
    });
    
    // 品牌图标悬停增强
    $('.modern-brand').hover(
        function() {
            $(this).find('.brand-icon').addClass('hover-effect');
        },
        function() {
            $(this).find('.brand-icon').removeClass('hover-effect');
        }
    );
    
    // 管理员徽章脉冲动画
    if ($('.admin-badge').length) {
        setInterval(function() {
            $('.admin-badge').addClass('pulse');
            setTimeout(function() {
                $('.admin-badge').removeClass('pulse');
            }, 500);
        }, 3000);
    }
    
    // 下拉菜单增强动画
    $('.dropdown-toggle').on('show.bs.dropdown', function() {
        const dropdown = $(this).next('.dropdown-menu');
        dropdown.addClass('show-animation');
    });
    
    $('.dropdown-toggle').on('hide.bs.dropdown', function() {
        const dropdown = $(this).next('.dropdown-menu');
        dropdown.removeClass('show-animation');
    });
    
    // 导航项活跃状态增强
    $('.modern-nav-link.active').each(function() {
        $(this).find('.nav-icon').addClass('active-pulse');
    });
    
    // 管理员下拉菜单项悬停效果
    $('.modern-dropdown-item').hover(
        function() {
            $(this).find('.dropdown-icon').addClass('icon-bounce');
        },
        function() {
            $(this).find('.dropdown-icon').removeClass('icon-bounce');
        }
    );
    
    // 移动端菜单收起优化
    $('.modern-nav-link').click(function() {
        if ($(window).width() < 992) {
            setTimeout(function() {
                $('.navbar-collapse').collapse('hide');
            }, 300);
        }
    });
    
    // 添加动态样式
    addNavbarDynamicStyles();
}

// 添加导航栏动态样式
function addNavbarDynamicStyles() {
    $('<style>')
        .prop('type', 'text/css')
        .html(`
            /* 导航栏动态样式 */
            .nav-ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: scale(0);
                animation: nav-ripple 0.6s linear;
                pointer-events: none;
                z-index: 1;
                /* 防止抖动 */
                transform-origin: center;
                will-change: transform, opacity;
            }
            
            @keyframes nav-ripple {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
            
            .toggler-ripple {
                position: absolute;
                top: 50%;
                left: 50%;
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.2);
                transform: translate(-50%, -50%) scale(0);
                animation: toggler-ripple 0.6s ease-out;
                pointer-events: none;
                /* 防止抖动 */
                will-change: transform, opacity;
            }
            
            @keyframes toggler-ripple {
                to {
                    transform: translate(-50%, -50%) scale(1);
                    opacity: 0;
                }
            }
            
            .admin-badge.pulse {
                animation: pulse-badge 0.5s ease-in-out;
                /* 防止抖动 */
                will-change: transform;
            }
            
            @keyframes pulse-badge {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.3); }
            }
            
            .show-animation {
                animation: dropdown-show 0.3s ease-out;
                /* 防止抖动 */
                will-change: transform, opacity;
            }
            
            @keyframes dropdown-show {
                0% {
                    opacity: 0;
                    transform: translateY(-10px) scale(0.95);
                }
                100% {
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }
            
            .hover-effect {
                animation: brand-hover 0.3s ease-in-out;
                /* 防止抖动 */
                will-change: transform;
            }
            
            @keyframes brand-hover {
                0%, 100% { transform: scale(1) rotate(0deg); }
                50% { transform: scale(1.1) rotate(10deg); }
            }
            
            .active-pulse {
                animation: active-pulse 2s ease-in-out infinite;
                /* 防止抖动 */
                will-change: transform, color, text-shadow;
            }
            
            @keyframes active-pulse {
                0%, 100% { 
                    transform: scale(1);
                    color: #ffd700;
                }
                50% { 
                    transform: scale(1.1);
                    color: #ffed4e;
                    text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
                }
            }
            
            .icon-bounce {
                animation: icon-bounce 0.5s ease-in-out;
                /* 防止抖动 */
                will-change: transform;
            }
            
            @keyframes icon-bounce {
                0%, 100% { transform: scale(1) rotate(0deg); }
                25% { transform: scale(1.1) rotate(-5deg); }
                75% { transform: scale(1.1) rotate(5deg); }
            }
            
            /* 导航栏加载动画 */
            .navbar-loading {
                position: relative;
                overflow: hidden;
            }
            
            .navbar-loading::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                animation: navbar-loading 2s infinite;
            }
            
            @keyframes navbar-loading {
                0% { left: -100%; }
                100% { left: 100%; }
            }
            
            /* 悬停光效 */
            .modern-nav-link::after {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
                transition: left 0.5s;
                z-index: 0;
                /* 防止抖动 */
                will-change: left;
            }
            
            .modern-nav-link:hover::after {
                left: 100%;
            }
            
            /* 移动端优化 */
            @media (max-width: 991.98px) {
                .nav-ripple {
                    display: none;
                }
                
                .modern-nav-link {
                    margin: 0.3rem 0;
                }
                
                .show-animation {
                    animation: mobile-dropdown-show 0.3s ease-out;
                    /* 防止抖动 */
                    will-change: max-height, opacity;
                }
                
                @keyframes mobile-dropdown-show {
                    0% {
                        opacity: 0;
                        max-height: 0;
                    }
                    100% {
                        opacity: 1;
                        max-height: 500px;
                    }
                }
            }
        `)
        .appendTo('head');
}

// 回到顶部功能
function initializeBackToTop() {
    const backToTopBtn = $('#backToTop');
    
    $(window).scroll(function() {
        if ($(this).scrollTop() > 300) {
            backToTopBtn.fadeIn();
        } else {
            backToTopBtn.fadeOut();
        }
    });
    
    backToTopBtn.click(function() {
        $('html, body').animate({
            scrollTop: 0
        }, 600);
        return false;
    });
}

// 搜索建议功能
function initializeSearchSuggestions() {
    const searchInput = $('input[name="query"]');
    let searchTimeout;
    
    if (searchInput.length === 0) return;
    
    // 创建建议容器
    const suggestionsContainer = $('<div class="search-suggestions"></div>');
    searchInput.parent().css('position', 'relative').append(suggestionsContainer);
    
    searchInput.on('input', function() {
        const query = $(this).val().trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 2) {
            suggestionsContainer.hide();
            return;
        }
        
        searchTimeout = setTimeout(function() {
            fetchSearchSuggestions(query, suggestionsContainer);
        }, 300);
    });
    
    // 点击其他地方隐藏建议
    $(document).click(function(e) {
        if (!$(e.target).closest('.search-suggestions, input[name="query"]').length) {
            suggestionsContainer.hide();
        }
    });
    
    // 键盘导航
    searchInput.keydown(function(e) {
        const suggestions = suggestionsContainer.find('.search-suggestion-item');
        const selected = suggestions.filter('.selected');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (selected.length === 0) {
                suggestions.first().addClass('selected');
            } else {
                selected.removeClass('selected');
                const next = selected.next();
                if (next.length) {
                    next.addClass('selected');
                } else {
                    suggestions.first().addClass('selected');
                }
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (selected.length === 0) {
                suggestions.last().addClass('selected');
            } else {
                selected.removeClass('selected');
                const prev = selected.prev();
                if (prev.length) {
                    prev.addClass('selected');
                } else {
                    suggestions.last().addClass('selected');
                }
            }
        } else if (e.key === 'Enter') {
            if (selected.length) {
                e.preventDefault();
                searchInput.val(selected.text());
                suggestionsContainer.hide();
            }
        } else if (e.key === 'Escape') {
            suggestionsContainer.hide();
        }
    });
}

// 获取搜索建议
function fetchSearchSuggestions(query, container) {
    $.ajax({
        url: '/search/api/suggestions',
        method: 'GET',
        data: { q: query },
        success: function(data) {
            displaySearchSuggestions(data, container);
        },
        error: function() {
            container.hide();
        }
    });
}

// 显示搜索建议
function displaySearchSuggestions(suggestions, container) {
    container.empty();
    
    if (suggestions.length === 0) {
        container.hide();
        return;
    }
    
    suggestions.forEach(function(suggestion) {
        const item = $(`
            <div class="search-suggestion-item" data-type="${suggestion.type}">
                <i class="fas fa-${suggestion.type === 'name' ? 'dna' : 'microscope'} me-2 text-muted"></i>
                ${suggestion.text}
                <small class="text-muted ms-auto">${suggestion.type === 'name' ? 'IS元素' : '宿主'}</small>
            </div>
        `);
        
        item.click(function() {
            $('input[name="query"]').val(suggestion.text);
            container.hide();
        });
        
        container.append(item);
    });
    
    container.show();
}

// 文件上传功能
function initializeFileUpload() {
    const fileUploadArea = $('.file-upload-area');
    const fileInput = $('input[type="file"]');
    
    if (fileUploadArea.length === 0) return;
    
    // 拖拽上传
    fileUploadArea.on('dragover', function(e) {
        e.preventDefault();
        $(this).addClass('dragover');
    });
    
    fileUploadArea.on('dragleave', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
    });
    
    fileUploadArea.on('drop', function(e) {
        e.preventDefault();
        $(this).removeClass('dragover');
        
        const files = e.originalEvent.dataTransfer.files;
        if (files.length > 0) {
            fileInput[0].files = files;
            displaySelectedFiles(files);
        }
    });
    
    // 点击上传
    fileUploadArea.click(function() {
        fileInput.click();
    });
    
    fileInput.change(function() {
        const files = this.files;
        if (files.length > 0) {
            displaySelectedFiles(files);
        }
    });
}

// 显示选中的文件
function displaySelectedFiles(files) {
    const fileList = $('.selected-files');
    if (fileList.length === 0) {
        $('.file-upload-area').after('<div class="selected-files mt-3"></div>');
    }
    
    $('.selected-files').empty();
    
    Array.from(files).forEach(function(file) {
        const fileItem = $(`
            <div class="alert alert-info d-flex justify-content-between align-items-center">
                <div>
                    <i class="fas fa-file me-2"></i>
                    <strong>${file.name}</strong>
                    <small class="text-muted ms-2">(${formatFileSize(file.size)})</small>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger remove-file">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `);
        
        fileItem.find('.remove-file').click(function() {
            fileItem.remove();
            $('input[type="file"]').val('');
        });
        
        $('.selected-files').append(fileItem);
    });
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 表单验证增强
function initializeFormValidation() {
    // 实时验证
    $('.needs-validation input, .needs-validation select, .needs-validation textarea').on('blur', function() {
        validateField($(this));
    });
    
    // 表单提交验证
    $('.needs-validation').submit(function(e) {
        const form = $(this);
        let isValid = true;
        
        form.find('input, select, textarea').each(function() {
            if (!validateField($(this))) {
                isValid = false;
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        form.addClass('was-validated');
    });
}

// 验证单个字段
function validateField(field) {
    const value = field.val().trim();
    const isRequired = field.prop('required');
    const fieldType = field.attr('type');
    let isValid = true;
    let errorMessage = '';
    
    // 必填验证
    if (isRequired && value === '') {
        isValid = false;
        errorMessage = '此字段为必填项';
    }
    
    // 邮箱验证
    if (fieldType === 'email' && value !== '') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = '请输入有效的邮箱地址';
        }
    }
    
    // 密码强度验证
    if (field.attr('name') === 'password' && value !== '') {
        if (value.length < 6) {
            isValid = false;
            errorMessage = '密码长度至少6个字符';
        }
    }
    
    // 显示验证结果
    const feedback = field.siblings('.invalid-feedback');
    if (isValid) {
        field.removeClass('is-invalid').addClass('is-valid');
        feedback.text('');
    } else {
        field.removeClass('is-valid').addClass('is-invalid');
        if (feedback.length === 0) {
            field.after(`<div class="invalid-feedback">${errorMessage}</div>`);
        } else {
            feedback.text(errorMessage);
        }
    }
    
    return isValid;
}

// 初始化工具提示
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 初始化数据表格
function initializeDataTables() {
    if ($('.data-table').length === 0) return;
    
    $('.data-table').each(function() {
        const table = $(this);
        
        // 基本配置
        const config = {
            responsive: true,
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.4/i18n/zh.json'
            },
            pageLength: 20,
            lengthMenu: [[10, 20, 50, 100], [10, 20, 50, 100]],
            order: [[0, 'asc']],
            columnDefs: [
                {
                    targets: 'no-sort',
                    orderable: false
                }
            ]
        };
        
        // 如果表格有特殊配置
        if (table.data('config')) {
            $.extend(config, table.data('config'));
        }
        
        table.DataTable(config);
    });
}

// 防止dropdown闪烁
function preventDropdownFlicker() {
    // 监听dropdown的show事件，确保只在用户操作时显示
    $('.dropdown-toggle').on('show.bs.dropdown', function(e) {
        // 如果不是用户点击触发的，阻止显示
        if (!e.clickEvent) {
            // 允许正常的用户交互
        }
    });
    
    // 确保页面加载完成后dropdown是关闭的
    setTimeout(function() {
        $('.dropdown-menu').removeClass('show');
        $('.dropdown-toggle').attr('aria-expanded', 'false');
    }, 0);
}

// 移动端菜单优化
function initializeMobileMenu() {
    // 移动端搜索切换
    $('.mobile-search-toggle').click(function() {
        $('.mobile-search-form').toggle();
    });
    
    // 点击菜单项后自动收起菜单
    $('.navbar-nav .nav-link').click(function() {
        const navbarToggler = $('.navbar-toggler');
        const navbarCollapse = $('.navbar-collapse');
        
        if (navbarToggler.is(':visible') && navbarCollapse.hasClass('show')) {
            navbarToggler.click();
        }
    });
}

// 通用AJAX错误处理
$(document).ajaxError(function(event, xhr, settings, thrownError) {
    console.error('AJAX Error:', thrownError);
    
    if (xhr.status === 403) {
        showAlert('您没有权限执行此操作', 'error');
    } else if (xhr.status === 404) {
        showAlert('请求的资源不存在', 'error');
    } else if (xhr.status === 500) {
        showAlert('服务器内部错误，请稍后重试', 'error');
    } else if (xhr.status === 0) {
        showAlert('网络连接错误，请检查网络设置', 'error');
    }
});

// 显示警告消息
function showAlert(message, type = 'info', duration = 5000) {
    const alertClass = type === 'error' ? 'alert-danger' : 
                      type === 'success' ? 'alert-success' : 
                      type === 'warning' ? 'alert-warning' : 'alert-info';
    
    const alert = $(`
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append(alert);
    
    // 自动消失
    if (duration > 0) {
        setTimeout(function() {
            alert.alert('close');
        }, duration);
    }
}

// 确认对话框
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// 格式化日期时间
function formatDateTime(dateString, format = 'YYYY-MM-DD HH:mm') {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return format.replace('YYYY', year)
                 .replace('MM', month)
                 .replace('DD', day)
                 .replace('HH', hours)
                 .replace('mm', minutes);
}

// 复制到剪贴板
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showAlert('已复制到剪贴板', 'success', 2000);
        });
    } else {
        // 兼容旧浏览器
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showAlert('已复制到剪贴板', 'success', 2000);
    }
}

// 加载指示器
function showLoading(element) {
    element.prop('disabled', true);
    const originalText = element.text();
    element.data('original-text', originalText);
    element.html('<span class="loading-spinner me-2"></span>加载中...');
}

function hideLoading(element) {
    element.prop('disabled', false);
    const originalText = element.data('original-text');
    if (originalText) {
        element.text(originalText);
    }
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 导出常用函数到全局
window.proISDB = {
    showAlert,
    confirmAction,
    formatDateTime,
    copyToClipboard,
    showLoading,
    hideLoading,
    debounce,
    throttle
};
