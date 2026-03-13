# 此文件可被视为一个工具类或模块，其核心功能已在GestureEngine中实现。
import numpy as np


class DynamicRecognizer:
    """
    一个封装了动态手势识别逻辑的类，由GestureEngine调用。
    """

    def __init__(self, model_path):
        self.model = None
        self.load_model(model_path)

    def load_model(self, model_path):
        try:
            from tensorflow.keras.models import load_model
            self.model = load_model(model_path)
        except Exception as e:
            print(f"加载动态识别LSTM模型失败: {e}")

    def recognize(self, trajectory_features, threshold=0.7):
        """
        Recognizes a dynamic gesture from a sequence of features.
        :param trajectory_features: A list of feature arrays, shape (seq_len, num_features)
        :param threshold: Confidence threshold
        :return: gesture_name, confidence
        """
        if self.model is None or len(trajectory_features) == 0:
            return None, 0.0

        features_array = np.expand_dims(np.array(trajectory_features), axis=0)  # Shape: (1, seq_len, features)

        prob_dist = self.model.predict(features_array)[0]
        max_prob = np.max(prob_dist)
        predicted_class_id = np.argmax(prob_dist)

        gesture_names = ['circle', 'line_left', 'line_right', 'up_line', 'down_line', 'Z']

        if max_prob > threshold and predicted_class_id < len(gesture_names):
            gesture_name = gesture_names[predicted_class_id]
            return gesture_name, max_prob

        return None, 0.0