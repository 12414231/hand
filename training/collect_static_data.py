import cv2
import mediapipe as mp
import os
import numpy as np
from config import STATIC_DATASET_DIR
from utilsss.feature_extractor import FeatureExtractor


def collect_static_data():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=True,  # 静态模式，适用于单帧
        max_num_hands=1,
        min_detection_confidence=0.7
    )
    cap = cv2.VideoCapture(0)

    # 定义手势类别
    gesture_labels = ["open_palm", "fist", "thumb_up", "thumb_down", "pinch",
                      "two_fingers", "three_fingers", "four_fingers",
                      "split_fingers", "call_gesture"]

    # 创建数据集目录
    os.makedirs(STATIC_DATASET_DIR, exist_ok=True)
    for label in gesture_labels:
        os.makedirs(os.path.join(STATIC_DATASET_DIR, label), exist_ok=True)

    feature_extractor = FeatureExtractor()
    sample_count = {label: 0 for label in gesture_labels}

    print("数据收集开始！")
    print("按对应的数字键收集手势数据:")
    for i, label in enumerate(gesture_labels):
        print(f"  {i}: {label}")
    print("按 'q' 退出。")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

                # 获取关键点坐标
                h, w, _ = frame.shape
                landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]

                cv2.putText(frame, "Ready to capture!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Collect Static Data', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        # 检查按键
        if ord('0') <= key <= ord('9'):
            idx = key - ord('0')
            if idx < len(gesture_labels):
                gesture_name = gesture_labels[idx]

                # 提取特征并保存
                features = feature_extractor.extract_static_features(landmarks)
                if features:
                    filepath = os.path.join(STATIC_DATASET_DIR, gesture_name, f"{sample_count[gesture_name]:04d}.npy")
                    np.save(filepath, features)
                    sample_count[gesture_name] += 1
                    print(f"Saved sample for '{gesture_name}' -> {filepath}")

    cap.release()
    cv2.destroyAllWindows()
    print("\n数据收集完成!")
    for label, count in sample_count.items():
        print(f"  {label}: {count} samples")


if __name__ == "__main__":
    collect_static_data()