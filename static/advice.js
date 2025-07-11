// static/advice.js

const scenarioSelect = document.getElementById("scenarioSelect");
const adviceSummary = document.getElementById("adviceSummary");
const emotionChart = document.getElementById("emotionChart").getContext("2d");

let chart; // chart.js instance

const emotionLabels = ["Angry", "Disgust", "Fear", "Happy", "Sad", "Surprise", "Neutral"];

// Template-based advice mappings
const adviceTemplates = {
  interview: {
    Happy: "Great! Smiling builds confidence during interviews.",
    Neutral: "Try using more facial expression and eye contact to appear confident.",
    Sad: "Practice positive affirmations before speaking.",
    Fear: "Simulate interviews to build comfort and reduce anxiety.",
    Angry: "Pause and breathe before answering under pressure."
  },
  exam: {
    Happy: "Being calm and happy is a sign of strong preparation.",
    Fear: "Try mock exams under time constraints.",
    Sad: "Ensure proper rest and maintain positivity.",
    Angry: "Take short breaks to manage frustration."
  },
  public: {
    Surprise: "Focus on staying composed; rehearse your speech.",
    Neutral: "Add more enthusiasm to better engage your audience.",
    Sad: "Positive body language helps convey energy.",
    Fear: "Start with deep breathing and rehearsal in front of friends."
  }
};

// Read log and trigger updates
fetch("/logs/emotion_log.jsonl")
  .then(res => res.text())
  .then(raw => {
    const lines = raw.trim().split("\n");
    const data = lines.map(line => JSON.parse(line));
    scenarioSelect.addEventListener("change", () => updateAdvice(data));
    updateAdvice(data); // initial load
  });

function updateAdvice(logData) {
  const selected = scenarioSelect.value;
  const filtered = selected === "all"
    ? logData
    : logData.filter(entry => entry.scenario === selected);

  if (filtered.length === 0) {
    adviceSummary.innerHTML = `<p class="text-red-500">No emotion records found for this scenario.</p>`;
    if (chart) chart.destroy();
    return;
  }

  const emotionCounts = {};
  const timestamps = [];
  const emotionTimeline = [];

  filtered.forEach(entry => {
    const emotion = entry.emotion;
    emotionCounts[emotion] = (emotionCounts[emotion] || 0) + 1;
    timestamps.push(new Date(entry.timestamp).toLocaleTimeString());
    emotionTimeline.push(emotionLabels.indexOf(emotion));
  });

  const mostFrequentEmotion = Object.entries(emotionCounts).reduce((a, b) => (a[1] > b[1] ? a : b))[0];
  const summaryText = generateAdvice(selected, mostFrequentEmotion);

  // Update advice section
  adviceSummary.innerHTML = `
    <p><strong>Scenario:</strong> ${selected}</p>
    <p><strong>Most Detected Emotion:</strong> ${mostFrequentEmotion}</p>
    <p class="mt-2 bg-blue-50 text-blue-700 px-4 py-2 rounded">${summaryText}</p>
  `;

  // Render Chart
  if (chart) chart.destroy();
  chart = new Chart(emotionChart, {
    type: 'line',
    data: {
      labels: timestamps,
      datasets: [{
        label: 'Emotion Index (0=Angry → 6=Neutral)',
        data: emotionTimeline,
        borderColor: 'rgba(99,102,241,1)',
        backgroundColor: 'rgba(99,102,241,0.1)',
        tension: 0.3,
        fill: true,
        pointRadius: 3
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          min: 0,
          max: 6,
          ticks: {
            callback: function(value) {
              return emotionLabels[value] || value;
            }
          }
        }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });
}

function generateAdvice(scenario, emotion) {
  if (!adviceTemplates[scenario]) {
    return "Keep tracking your emotions for smarter insights.";
  }
  return adviceTemplates[scenario][emotion] || "Stay emotionally aware and balanced.";
}
