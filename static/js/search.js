/**
 * search.js – Real-time search filtering for cards/tables.
 * Uses a debounce to avoid excessive DOM operations.
 */
document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    let timeout = null;

    searchInput.addEventListener('input', function () {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            const query = this.value.toLowerCase().trim();
            const items = document.querySelectorAll('.searchable-item');

            if (!items.length) return;

            let visibleCount = 0;
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                const match = text.includes(query);
                item.style.display = match ? '' : 'none';
                if (match) visibleCount++;
            });

            // Show/hide "no results" message
            const noResults = document.getElementById('noSearchResults');
            if (noResults) {
                noResults.style.display = visibleCount === 0 ? 'block' : 'none';
            }
        }, 300);
    });
});