<link rel="stylesheet" href="../../style/style.css">

<div class="toc-page" data-date="">
    <h1 class="toc-page-title">目次</h1>
    <div class="toc">
        <div class="toc-title">目次</div>
        <ul>
            <li><a href="Modbus_使用方法.jp.md">ROS2 Modbus 使用方法ガイド</a></li>
            <li><a href="Modbus_Usage_Guide.en.md">ROS2 Modbus Usage Guide (English)</a></li>
            <li><a href="Modbus_使用方法.cn.md">ROS2 Modbus 使用方法指南 (中文)</a></li>
        </ul>
    </div>
</div>

<!-- Footer -->
<div class="footer">
    <div class="footer-doc-name">Modbus ドキュメント</div>
    <img class="footer-logo" src="../../style/TechShare_logo.svg" alt="TechShare Logo">
</div>

<script>
    // Update document name in footer
    document.addEventListener('DOMContentLoaded', function() {
        const docPath = window.location.pathname;
        const docName = docPath.split('/').pop().replace('.md', '').replace('.jp', '');
        const docNameElement = document.querySelector('.footer-doc-name');
        if (docNameElement) {
            docNameElement.textContent = docName + ' ドキュメント';
        }
        
        // Set current date
        const tocPageElement = document.querySelector('.toc-page');
        if (tocPageElement) {
            const today = new Date();
            const dateString = today.toLocaleDateString('ja-JP');
            tocPageElement.setAttribute('data-date', dateString);
        }
    });
</script>