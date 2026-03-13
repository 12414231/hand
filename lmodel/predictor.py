# lmodel/predictor.py
import pickle
import numpy as np

class StaticGesturePredictor:
    def __init__(self, model_path):
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

    def predict(self, landmarks):
        """
        预测静态手势。
        landmarks: [x1,y1,z1, x2,y2,z2, ...] (63维)
        """
        features = np.array(landmarks).reshape(1, -1)
        prediction = self.model.predict(features)[0]
        # confidence = max(self.model.predict_proba(features)[0]) # 如果需要，可以在别处获取
        # 返回纯净的标签，不带置信度
        return prediction

class DynamicGesturePredictor:
    def __init__(self, model_path):
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

    def predict(self, trajectory):
        """
        预测动态手势。
        trajectory: [[x1,y1], [x2,y2], ...] (N x 2)
        """
        from training.train_dynamic_model_from_npy import calculate_dynamic_features
        features = calculate_dynamic_features(trajectory).reshape(1, -1)
        prediction = self.model.predict(features)[0]
        # 注意：RandomForest没有predict_proba，这里用predict代替
        # 如果需要概率，可以使用其他模型或修改
        return prediction