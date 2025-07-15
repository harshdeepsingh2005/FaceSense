import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay, roc_auc_score, roc_curve, accuracy_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import label_binarize
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.datasets import cifar10  # or replace with actual dataset

# Load your trained model
model = load_model("models/emotiondetector.h5")

# Load dataset (replace with your own dataset if needed)
(X_train, y_train), (X_test, y_test) = cifar10.load_data()

# Preprocess
X_test = X_test.astype("float32") / 255.0
y_test = y_test.flatten()
y_test_cat = to_categorical(y_test, num_classes=10)

# Predict
y_probs = model.predict(X_test)
y_preds = np.argmax(y_probs, axis=1)

# Metrics
print("Accuracy:", accuracy_score(y_test, y_preds))
print("Precision:", precision_score(y_test, y_preds, average='weighted'))
print("Recall:", recall_score(y_test, y_preds, average='weighted'))
print("F1 Score:", f1_score(y_test, y_preds, average='weighted'))
print("\nClassification Report:\n", classification_report(y_test, y_preds))

# Confusion Matrix
cm = confusion_matrix(y_test, y_preds)
fig, ax = plt.subplots(figsize=(10, 8))
disp = ConfusionMatrixDisplay(confusion_matrix=cm)
disp.plot(cmap="Blues", ax=ax)
plt.title("Confusion Matrix")
plt.show()

# Optional: ROC Curve (for multiclass, one-vs-all)
try:
    fpr = dict()
    tpr = dict()
    roc_auc = dict()
    for i in range(10):
        fpr[i], tpr[i], _ = roc_curve(y_test_cat[:, i], y_probs[:, i])
        roc_auc[i] = roc_auc_score(y_test_cat[:, i], y_probs[:, i])

    plt.figure(figsize=(10, 8))
    for i in range(10):
        plt.plot(fpr[i], tpr[i], label=f"Class {i} (AUC = {roc_auc[i]:.2f})")
    plt.plot([0, 1], [0, 1], "k--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve - Multiclass")
    plt.legend(loc="lower right")
    plt.grid(True)
    plt.show()
except Exception as e:
    print("ROC curve generation failed:", e)
