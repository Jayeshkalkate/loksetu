/**
 * charts.js – Render all dashboard charts.
 * Expects these global variables from Django template:
 *   window.complaintStatus = { pending: 10, inProgress: 5, resolved: 20 }
 *   window.districtData = [ { district: "Mumbai", count: 15 }, ... ]
 *   window.trendLabels = ["Jan", "Feb", ...]
 *   window.trendValues = [10, 20, ...]
 *   window.fundData = { total: 100000, used: 40000, remaining: 60000 }
 */

document.addEventListener('DOMContentLoaded', function () {
    // ----- Status Pie Chart -----
    const statusChartEl = document.getElementById('statusChart');
    if (statusChartEl && window.complaintStatus) {
        const labels = Object.keys(window.complaintStatus);
        const data = Object.values(window.complaintStatus);
        if (labels.length && data.some(v => v > 0)) {
            new Chart(statusChartEl, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' },
                        title: { display: true, text: 'Complaint Status Breakdown' }
                    }
                }
            });
        } else {
            statusChartEl.parentElement.innerHTML = '<p class="text-muted">No complaint data available.</p>';
        }
    }

    // ----- District Bar Chart -----
    const districtChartEl = document.getElementById('districtChart');
    if (districtChartEl && window.districtData && window.districtData.length) {
        const districts = window.districtData.map(d => d.district || 'Unknown');
        const counts = window.districtData.map(d => d.count || 0);
        new Chart(districtChartEl, {
            type: 'bar',
            data: {
                labels: districts,
                datasets: [{
                    label: 'Complaints per District',
                    data: counts,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                },
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'District-wise Complaints' }
                }
            }
        });
    }

    // ----- Trend Line Chart -----
    const trendChartEl = document.getElementById('trendChart');
    if (trendChartEl && window.trendLabels && window.trendValues) {
        new Chart(trendChartEl, {
            type: 'line',
            data: {
                labels: window.trendLabels,
                datasets: [{
                    label: 'Complaints Over Time',
                    data: window.trendValues,
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: 'Complaint Trend' }
                }
            }
        });
    }

    // ----- Fund Analysis Bar/Pie Charts -----
    const fundChartEl = document.getElementById('fundChart');
    if (fundChartEl && window.fundData) {
        new Chart(fundChartEl, {
            type: 'bar',
            data: {
                labels: ['Total', 'Used', 'Remaining'],
                datasets: [{
                    label: 'Funds (₹)',
                    data: [
                        window.fundData.total || 0,
                        window.fundData.used || 0,
                        window.fundData.remaining || 0
                    ],
                    backgroundColor: ['#4CAF50', '#FF9800', '#2196F3'],
                    borderColor: ['#388E3C', '#F57C00', '#1976D2'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                },
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Fund Overview' }
                }
            }
        });
    }

    // Fund Pie Chart (used vs remaining)
    const pieChartEl = document.getElementById('pieChart');
    if (pieChartEl && window.fundData) {
        const used = window.fundData.used || 0;
        const remaining = window.fundData.remaining || 0;
        if (used + remaining > 0) {
            new Chart(pieChartEl, {
                type: 'pie',
                data: {
                    labels: ['Used', 'Remaining'],
                    datasets: [{
                        data: [used, remaining],
                        backgroundColor: ['#FF9800', '#4CAF50'],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' },
                        title: { display: true, text: 'Fund Utilisation' }
                    }
                }
            });
        } else {
            pieChartEl.parentElement.innerHTML = '<p class="text-muted">No fund data available.</p>';
        }
    }
});