# 🎭 FaceSense AI – Real-Time Facial Emotion Recognition with Scenario-Aware Insights

[Click here for Project Report](https://1drv.ms/w/c/E5707C7E5563C887/EaWcaFzXz_VEkQHJWVOXALsBU64MflwrK4ASbssH4WU-jg?e=uAokNr)

FaceSense is a modular AI-powered facial emotion detection system using deep learning and OpenCV. It supports real-time webcam-based emotion recognition, image upload predictions, and provides scenario-specific advice based on emotion patterns.

---

## 🚀 Features

- 🔍 Real-time **emotion detection** from webcam and image uploads  
- 📸 **Live camera feed** with confidence meter and emoji overlay  
- 📁 Logs emotion data to separate files:  
  - `live_log.jsonl` (webcam)  
  - `upload_log.jsonl` (image uploads)  
- 🎭 **Scenario selection** before live detection (Interview, Exam, Public Speaking, etc.)  
- 🧠 **Personalized advice page** with emotion chart and context-aware tips  
- 📊 **Analytics page** with emotion frequency charts and history logs  
- 📂 **Only latest 5 sessions retained** to reduce log clutter  
- 💾 **Session-wise filtering** in Analytics and Advice pages  
- 🌗 Dark mode toggle, animated UI, hover effects, and more  

---

## 🧱 Tech Stack

- Python (Flask)  
- TensorFlow/Keras (CNN model)  
- OpenCV (face detection)  
- HTML5, Tailwind CSS  
- JavaScript (Chart.js for graphs)  

---

## 📁 Project Structure

```
emotion_detection/
├── app.py                    # Flask backend
├── templates/
│   ├── index.html            # Main detection page
│   ├── scenario.html         # Scenario selection
│   ├── advice.html           # Emotion advice + chart
│   └── analytics.html        # Session-wise emotion analysis
├── static/
│   ├── styles.css            # Custom UI styles
│   └── script.js             # Client-side detection + rendering
├── models/
│   └── emotiondetector.h5    # Pre-trained CNN model
├── logs/
│   ├── live_log.jsonl        # Webcam session logs (max 5 sessions)
│   └── upload_log.jsonl      # Image upload logs
```

---

## 🧪 How to Run

1. **Install dependencies:**

```bash
pip install flask opencv-python tensorflow
```

2. **Place your model** in `models/emotiondetector.h5`.

3. **Run the app:**

```bash
python app.py
```

4. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🎯 Advanced Features

- **Session-Based Advice:** Each webcam session is tagged with a UUID and scenario. The `/advice.html` page analyzes the dominant emotion for the selected session.
- **Scenario-Aware Tips:** Advice adapts based on the context (Interview, Exam, Public Speaking, etc.).
- **Live Analytics Filtering:** Users can filter by:
  - `Source` (upload / webcam)
  - `Session ID` (latest 5 only)

---

## 🗃 Example Session Log

```json
{
  "timestamp": "2025-07-10 20:22:13",
  "source": "webcam",
  "emotion": "Fear",
  "confidence": 0.91,
  "session_id": "a8123e32-4cc5-4d82-9442-7f2e7a705ccc",
  "scenario": "interview"
}
```

---

## 📌 Notes

- Sessions are pruned to retain **only the latest 5**, automatically.
- All logs are stored in `.jsonl` format (1 JSON object per line).
- Make sure to select a **scenario before starting live detection**.
- For local analytics, `localStorage` may cache old results — clear it to refresh history.

---

## 📷 Screenshots 

![Confusion matrix](https://github.com/user-attachments/assets/762bf7b3-c9b1-483e-a480-e1e7a0a37e08)

![ROC curve](https://github.com/user-attachments/assets/1a7410ab-ed80-4950-af6d-6265c0ed0220)

![Classification report](https://github.com/user-attachments/assets/397b67c4-4bc1-48f8-8dca-aac01971b955)

---

## 🤝 Contributors

- Harshdeep Singh, Vaibhav Mohanty, Kirti Thakur and Aditya Vardhan
- Model credit: FER2013
  
---

## 📄 License

MIT License – free to use, modify, and distribute.

