document.addEventListener("DOMContentLoaded", () => {
  const imageInput = document.getElementById("imageInput");
  const preview = document.getElementById("preview");
  const form = document.getElementById("uploadForm");
  const result = document.getElementById("result");
  const loading = document.getElementById("loading");
  const startBtn = document.getElementById("startBtn");
  const stopBtn = document.getElementById("stopBtn");
  const liveFeed = document.getElementById("liveFeed");
  const confidenceBar = document.getElementById("confidenceBar");
  const history = document.getElementById("history");
  const darkToggle = document.getElementById("darkToggle");
  const scenarioSelect = document.getElementById("scenarioSelect"); // From scenario.html
  const startScenarioBtn = document.getElementById("startScenarioBtn"); // From scenario.html

  const emotionEmojis = {
    Angry: "😠",
    Disgust: "🤢",
    Fear: "😨",
    Happy: "😄",
    Sad: "😢",
    Surprise: "😲",
    Neutral: "😐"
  };

  // Preview image
  imageInput?.addEventListener("change", () => {
    const file = imageInput.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        preview.src = e.target.result;
        preview.classList.remove("hidden");
      };
      reader.readAsDataURL(file);
    } else {
      preview.classList.add("hidden");
    }
  });

  // Upload form
  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = imageInput.files[0];
    if (!file) return alert("Please select an image first.");

    const formData = new FormData();
    formData.append("image", file);

    result.textContent = "";
    loading.classList.remove("hidden");

    try {
      const res = await fetch("/predict", {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      loading.classList.add("hidden");

      if (res.ok) {
        const emoji = emotionEmojis[data.emotion] || "";
        result.innerHTML = `Detected Emotion: <strong>${data.emotion} ${emoji}</strong><br>Confidence: ${(data.confidence * 100).toFixed(2)}%`;
        confidenceBar.style.width = `${data.confidence * 100}%`;

        const timestamp = new Date().toLocaleTimeString();
        const logItem = `<li>${timestamp}: ${data.emotion} ${emoji}</li>`;
        history.innerHTML = logItem + history.innerHTML;

        const log = JSON.parse(localStorage.getItem("emotionLog") || "[]");
        log.unshift({
          emotion: data.emotion,
          emoji: emoji,
          confidence: data.confidence,
          time: timestamp
        });
        localStorage.setItem("emotionLog", JSON.stringify(log));

        if (["Angry", "Fear"].includes(data.emotion) && navigator.vibrate) {
          navigator.vibrate(500);
        }

      } else {
        result.textContent = data.error || "Something went wrong.";
        confidenceBar.style.width = "0%";
      }
    } catch (err) {
      console.error(err);
      result.textContent = "Error connecting to the server.";
      loading.classList.add("hidden");
      confidenceBar.style.width = "0%";
    }
  });

  // Start Live Feed
  startBtn?.addEventListener("click", () => {
    fetch("/start_session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario: "Default" }) // fallback
    }).then(() => {
      liveFeed.src = "/video_feed";
    });
  });

  // Stop Live Feed
  stopBtn?.addEventListener("click", () => {
    liveFeed.src = "";
    fetch("/stop_camera");
  });

  // Dark Mode Toggle
  darkToggle?.addEventListener("change", () => {
    document.body.classList.toggle("dark");
  });

  // Scenario selection (from scenario.html)
  startScenarioBtn?.addEventListener("click", () => {
    const selected = scenarioSelect.value || "General";
    fetch("/start_session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario: selected })
    }).then(() => {
      window.location.href = "/";
    });
  });
});
