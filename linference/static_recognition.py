# 此文件可被视为一个工具类或模块，其核心功能已在GestureEngine中实现。
# 它不作为一个独立的执行单元，而是提供静态识别的逻辑。
import numpy as np


class StaticRecognizer:
    """
    一个封装了静态手势识别逻辑的类，由GestureEngine调用。
    """

    def __init__(self, model_path, scaler_path):
        self.model = None
        self.scaler = None
        self.load_model(model_path, scaler_path)

    def load_model(self, model_path, scaler_path):
        import joblib
        try:
            self.model = joblib.load(model_path)
            self.scaler = joblib.load(scaler_path)
        except Exception as e:
            print(f"加载静态识别模型失败: {e}")

    def recognize(self, features, threshold=0.7):
        if self.model is None or self.scaler is None:
            return None, 0.0

        features_scaled = self.scaler.transform([features])
        prob_dist = self.model.predict_proba(features_scaled)[0]
        max_prob = np.max(prob_dist)
        predicted_class_id = np.argmax(prob_dist)

        if max_prob > threshold:
            gesture_name = self.model.classes_[predicted_class_id]
            return gesture_name, max_prob

        return None, 0.0