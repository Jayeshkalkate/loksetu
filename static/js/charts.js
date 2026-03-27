// Bar Chart
const ctx = document.getElementById('fundChart');

if (ctx) {
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Total', 'Used', 'Remaining'],
      datasets: [{
        label: 'Fund Analysis',
        data: [
          window.totalFunds,
          window.totalUsed,
          window.remaining
        ]
      }]
    }
  });
}


// Pie Chart
const pie = document.getElementById('pieChart');

if (pie) {
  new Chart(pie, {
    type: 'pie',
    data: {
      labels: ['Used', 'Remaining'],
      datasets: [{
        data: [
          window.totalUsed,
          window.remaining
        ]
      }]
    }
  });
}