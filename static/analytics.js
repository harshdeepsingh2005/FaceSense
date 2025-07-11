document.addEventListener("DOMContentLoaded", () => {
  const emotionChartCtx = document.getElementById("emotionChart").getContext("2d");
  const historyList = document.getElementById("historyList");
  const resetBtn = document.getElementById("resetAnalytics");
  const exportBtn = document.getElementById("exportCSV");

  let pastEmotions = JSON.parse(localStorage.getItem("emotionLog") || "[]");

  const emotionCounts = {};
  pastEmotions.forEach(({ emotion }) => {
    emotionCounts[emotion] = (emotionCounts[emotion] || 0) + 1;
  });

  const labels = Object.keys(emotionCounts);
  const counts = Object.values(emotionCounts);

  const chart = new Chart(emotionChartCtx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Frequency',
        backgroundColor: '#6366f1',
        data: counts
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true, ticks: { stepSize: 1 } }
      }
    }
  });

  historyList.innerHTML = pastEmotions.map(item =>
    `<li>${item.time} — ${item.emotion} ${item.emoji}</li>`
  ).join("");

  // RESET
  resetBtn.addEventListener("click", () => {
    if (confirm("Clear all stored emotion analytics?")) {
      localStorage.removeItem("emotionLog");
      location.reload();
    }
  });

  // EXPORT
  exportBtn.addEventListener("click", () => {
    if (pastEmotions.length === 0) {
      alert("No data to export.");
      return;
    }

    const csvContent = [
      ["Time", "Emotion", "Confidence (%)"],
      ...pastEmotions.map(e => [e.time, e.emotion, (e.confidence * 100).toFixed(2)])
    ].map(e => e.join(",")).join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "emotion_analytics.csv";
    a.click();

    URL.revokeObjectURL(url);
  });
});
