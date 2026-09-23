/**
 * dashboard.js – Additional dashboard interactivity.
 * Can be merged with charts.js if desired, but kept separate for modularity.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Auto-refresh notification (example)
    const refreshBtn = document.getElementById('refreshDashboard');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function () {
            location.reload();
        });
    }

    // Toggle sidebar on mobile (Bootstrap or custom)
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function () {
            document.querySelector('.sidebar').classList.toggle('show');
        });
    }

    // Tooltip initialisation (if using Bootstrap)
    if (typeof bootstrap !== 'undefined') {
        const tooltips = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltips.map(el => new bootstrap.Tooltip(el));
    }

    console.log('Dashboard interactive elements initialised.');
});