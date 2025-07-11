import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping

# Paths for training and testing data
TRAIN_DIR = "train"
TEST_DIR = "test"
IMG_SIZE = 48
BATCH_SIZE = 32
NUM_CLASSES = 7

# Data Augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    zoom_range=0.2,
    brightness_range=[0.8, 1.2],
    horizontal_flip=True
)

test_datagen = ImageDataGenerator(rescale=1./255)  # No augmentation for testing

train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)

test_generator = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical'
)

# Transfer Learning: MobileNetV2
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
base_model.trainable = False  # Freeze base model layers initially

# Model Definition
model = Sequential([
    base_model,
    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(NUM_CLASSES, activation='softmax')
])

# Compile Model
optimizer = SGD(learning_rate=0.001, momentum=0.9)
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

# Callbacks
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6, verbose=1)
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train Model
history = model.fit(
    train_generator,
    validation_data=test_generator,
    epochs=25,
    callbacks=[reduce_lr, early_stopping]
)

# Fine-Tune Model (Unfreeze More Layers)
base_model.trainable = True
for layer in base_model.layers[:50]:  # Keep the first 50 layers frozen
    layer.trainable = False

model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

history_fine_tune = model.fit(
    train_generator,
    validation_data=test_generator,
    epochs=15,
    callbacks=[reduce_lr, early_stopping]
)

# Save Model
MODEL_PATH = "models/emotion_model_mobilenet.h5"
os.makedirs("models", exist_ok=True)
model.save(MODEL_PATH)
print(f"Model saved to {MODEL_PATH}")

# Evaluate Model
loss, accuracy = model.evaluate(test_generator)
print(f"Final Test Loss: {loss:.4f}, Final Test Accuracy: {accuracy:.4f}")
