from flask import Flask, render_template, Response, request, jsonify, send_from_directory
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from datetime import datetime
import os
import json
import uuid

app = Flask(__name__)

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Load model and assets
model = load_model("models/emotiondetector.h5")
emotion_classes = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Runtime state
camera = None
current_session_id = None
selected_scenario = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analytics.html')
def analytics():
    return render_template('analytics.html')

@app.route('/scenario.html')
def scenario():
    return render_template('scenario.html')

@app.route('/advice.html')
def advice():
    return render_template('advice.html')

@app.route('/start_session', methods=['POST'])
def start_session():
    global current_session_id, selected_scenario
    data = request.get_json()
    selected_scenario = data.get("scenario", "General")
    current_session_id = str(uuid.uuid4())
    prune_old_sessions()
    return jsonify({'session_id': current_session_id})

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return jsonify({'error': 'No face detected'}), 200

    x, y, w, h = faces[0]
    face_gray = gray[y:y+h, x:x+w]
    resized = cv2.resize(face_gray, (48, 48)) / 255.0
    reshaped = np.expand_dims(resized, axis=-1)
    reshaped = np.expand_dims(reshaped, axis=0)

    prediction = model.predict(reshaped)
    emotion_idx = np.argmax(prediction[0])
    confidence = float(prediction[0][emotion_idx])
    label = emotion_classes[emotion_idx]

    emoji = get_emoji(label)
    log_prediction(label, confidence, "upload")

    return jsonify({
        'emotion': label,
        'confidence': round(confidence, 2),
        'emoji': emoji
    })

def generate_frames():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()
        if not success:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            face_gray = gray[y:y+h, x:x+w]
            resized = cv2.resize(face_gray, (48, 48)) / 255.0
            reshaped = np.expand_dims(resized, axis=-1)
            reshaped = np.expand_dims(reshaped, axis=0)

            prediction = model.predict(reshaped)
            emotion_idx = np.argmax(prediction[0])
            confidence = float(prediction[0][emotion_idx])
            label = emotion_classes[emotion_idx]

            log_prediction(label, confidence, "webcam")

            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_camera')
def stop_camera():
    global camera
    if camera is not None:
        camera.release()
        camera = None
    return "Camera stopped", 200

# Serve JSONL log files to advice.html and others
@app.route('/logs/<path:filename>')
def serve_logs(filename):
    return send_from_directory("logs", filename)

# Emoji mapper
def get_emoji(emotion):
    mapping = {
        'Happy': '😊',
        'Sad': '😢',
        'Angry': '😠',
        'Fear': '😨',
        'Surprise': '😲',
        'Disgust': '🤢',
        'Neutral': '😐'
    }
    return mapping.get(emotion, '')

# Log entry function
def log_prediction(emotion, confidence, source):
    global current_session_id, selected_scenario

    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": source,
        "emotion": emotion,
        "confidence": round(confidence, 2),
        "session_id": current_session_id if source == "webcam" else None,
        "scenario": selected_scenario if source == "webcam" else None
    }

    log_file = "logs/live_log.jsonl" if source == "webcam" else "logs/upload_log.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

# Retain only last 5 sessions
def prune_old_sessions():
    path = "logs/live_log.jsonl"
    if not os.path.exists(path):
        return

    with open(path, "r") as f:
        lines = [json.loads(line) for line in f.readlines()]

    sessions = {}
    for entry in lines:
        sid = entry.get("session_id")
        if sid:
            sessions.setdefault(sid, []).append(entry)

    if len(sessions) > 5:
        latest_sessions = sorted(sessions.items(), key=lambda x: x[1][0]["timestamp"], reverse=True)[:5]
        new_logs = []
        for _, entries in latest_sessions:
            new_logs.extend(entries)

        with open(path, "w") as f:
            for entry in new_logs:
                f.write(json.dumps(entry) + "\n")

@app.route('/get_sessions')
def get_sessions():
    path = "logs/live_log.jsonl"
    if not os.path.exists(path):
        return jsonify([])

    with open(path, "r") as f:
        lines = [json.loads(line) for line in f.readlines()]

    sessions = {}
    for entry in lines:
        sid = entry.get("session_id")
        if sid:
            sessions.setdefault(sid, {
                "session_id": sid,
                "scenario": entry.get("scenario", "General"),
                "start_time": entry["timestamp"]
            })

    # Return last 5 session dicts sorted by start time descending
    sorted_sessions = sorted(sessions.values(), key=lambda x: x["start_time"], reverse=True)
    return jsonify(sorted_sessions[:5])


@app.route('/get_session_logs/<session_id>')
def get_session_logs(session_id):
    path = "logs/live_log.jsonl"
    if not os.path.exists(path):
        return jsonify([])

    with open(path, "r") as f:
        lines = [json.loads(line) for line in f.readlines()]

    filtered = [entry for entry in lines if entry.get("session_id") == session_id]
    return jsonify(filtered)


# Run app
if __name__ == '__main__':
    app.run(debug=True)
