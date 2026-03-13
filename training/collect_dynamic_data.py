import cv2
import mediapipe as mp
import os
import numpy as np
from config import DYNAMIC_DATASET_DIR, MAX_TRAJECTORY_LENGTH
from utilsss.trajectory_buffer import TrajectoryBuffer
from utilsss.feature_extractor import FeatureExtractor


def collect_dynamic_data():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.5
    )
    cap = cv2.VideoCapture(0)

    gesture_labels = ["circle", "line_left", "line_right", "up_line", "down_line", "Z"]

    os.makedirs(DYNAMIC_DATASET_DIR, exist_ok=True)
    for label in gesture_labels:
        os.makedirs(os.path.join(DYNAMIC_DATASET_DIR, label), exist_ok=True)

    trajectory_buffer = TrajectoryBuffer(max_length=MAX_TRAJECTORY_LENGTH)
    feature_extractor = FeatureExtractor()
    sample_count = {label: 0 for label in gesture_labels}

    print("动态数据收集开始！")
    print("按对应的数字键收集轨迹数据:")
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

                h, w, _ = frame.shape
                landmarks = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]
                trajectory_buffer.add(landmarks)

                status_text = f"Trajectory Length: {trajectory_buffer.size()}"
                cv2.putText(frame, status_text, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow('Collect Dynamic Data', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        # 检查按键
        if ord('0') <= key <= ord('9'):
            idx = key - ord('0')
            if idx < len(gesture_labels):
                gesture_name = gesture_labels[idx]

                # 获取完整轨迹并提取特征
                trajectory = trajectory_buffer.get_trajectory()
                if len(trajectory) >= 8:  # 至少8帧才能算作有效轨迹
                    # 为了统一输入，我们将轨迹填充或截断到固定长度
                    if len(trajectory) < MAX_TRAJECTORY_LENGTH:
                        # 用最后一帧填充
                        last_frame = trajectory[-1]
                        while len(trajectory) < MAX_TRAJECTORY_LENGTH:
                            trajectory.append(last_frame)
                    elif len(trajectory) > MAX_TRAJECTORY_LENGTH:
                        # 截断到最大长度
                        trajectory = trajectory[-MAX_TRAJECTORY_LENGTH:]

                    # 提取特征序列
                    features_sequence = []
                    for frame_landmarks in trajectory:
                        features = feature_extractor.extract_static_features(frame_landmarks)
                        features_sequence.append(features)

                    filepath = os.path.join(DYNAMIC_DATASET_DIR, gesture_name, f"{sample_count[gesture_name]:04d}.npy")
                    np.save(filepath, features_sequence)
                    sample_count[gesture_name] += 1
                    print(f"Saved trajectory sample for '{gesture_name}' -> {filepath}")

                    trajectory_buffer.clear()  # 保存后清空缓冲区

    cap.release()
    cv2.destroyAllWindows()
    print("\n动态数据收集完成!")
    for label, count in sample_count.items():
        print(f"  {label}: {count} samples")


if __name__ == "__main__":
    collect_dynamic_data()