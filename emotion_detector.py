import cv2
import numpy as np
from deepface import DeepFace


def detect_emotion(frame):
    # Make prediction (replace with your model's predict call)
    analysis = DeepFace.analyze(
        img_path=frame,
        actions=["age", "gender", "race", "emotion"],
    )
    print(analysis)

    return analysis
