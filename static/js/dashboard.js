document.addEventListener("DOMContentLoaded", () => {
  // Pie Chart
  new Chart(document.getElementById("statusChart"), {
    type: "pie",
    data: {
      labels: Object.keys(statusData),
      datasets: [
        {
          data: Object.values(statusData),
        },
      ],
    },
  });

  // Bar Chart
  new Chart(document.getElementById("districtChart"), {
    type: "bar",
    data: {
      labels: districtData.map((d) => d.district),
      datasets: [
        {
          label: "Complaints",
          data: districtData.map((d) => d.count),
        },
      ],
    },
  });

  // Line Chart
  new Chart(document.getElementById("trendChart"), {
    type: "line",
    data: {
      labels: trendLabels,
      datasets: [
        {
          label: "Complaints",
          data: trendValues,
        },
      ],
    },
  });
});
