// 自动处理.md后缀的URL重定向
document.addEventListener('DOMContentLoaded', function () {
    // 检查URL是否包含.md后缀
    const currentPath = window.location.pathname;

    if (currentPath.endsWith('.md')) {
        // 移除 .md 后缀
        const newPath = currentPath.substring(0, currentPath.length - 3);

        // 执行重定向
        const newUrl = window.location.origin + newPath;
        console.log('Redirecting from ' + currentPath + ' to ' + newPath);
        window.location.replace(newUrl);
    }
});