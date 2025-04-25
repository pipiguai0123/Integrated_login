// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 自动隐藏提示消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 1s';
            alert.style.opacity = '0';
            setTimeout(function() {
                alert.remove();
            }, 1000);
        }, 3000);
    });
    
    // 确认删除操作
    const deleteForms = document.querySelectorAll('form[onsubmit]');
    deleteForms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            const confirmed = confirm('确定要执行此删除操作吗？');
            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
});
