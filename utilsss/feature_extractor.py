import numpy as np


class FeatureExtractor:
    @staticmethod
    def extract_static_features(landmarks):
        """
        从手部关键点提取静态手势特征。
        特征包括相对于手腕的归一化坐标。
        """
        if not landmarks or len(landmarks) != 21:
            return []

        wrist = landmarks[0]  # 手腕作为参考点
        features = []
        for point in landmarks:
            # 相对于手腕的偏移
            dx = point[0] - wrist[0]
            dy = point[1] - wrist[1]
            features.extend([dx, dy])

        return features

    @staticmethod
    def extract_dynamic_features(trajectory_landmarks):
        """
        从一系列关键点轨迹中提取动态手势特征。
        例如，计算质心、速度、方向等。
        """
        if len(trajectory_landmarks) < 2:
            return []

        features = []
        for i in range(1, len(trajectory_landmarks)):
            prev_frame = trajectory_landmarks[i - 1]
            curr_frame = trajectory_landmarks[i]

            frame_features = []
            for j in range(len(prev_frame)):
                px, py = prev_frame[j]
                cx, cy = curr_frame[j]
                vx = cx - px  # 速度x
                vy = cy - py  # 速度y
                frame_features.extend([vx, vy])

            features.append(frame_features)

        # 将序列展平，或取平均值等，取决于后续模型输入
        if features:
            # 取所有帧特征的平均值作为最终特征向量
            avg_features = np.mean(features, axis=0)
            return avg_features.tolist()

        return []