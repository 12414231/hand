import os

# --- 项目路径配置 ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TRAINING_DIR = os.path.join(PROJECT_ROOT, "training")
DATASET_DIR = os.path.join(TRAINING_DIR, "dataset")
STATIC_DATASET_DIR = os.path.join(DATASET_DIR, "static")
DYNAMIC_DATASET_DIR = os.path.join(DATASET_DIR, "dynamic")
MODELS_DIR = os.path.join(TRAINING_DIR, "models")
STATIC_MODEL_PATH = os.path.join(MODELS_DIR, "static_gesture_model.pkl")
LSTM_MODEL_PATH = os.path.join(MODELS_DIR, "lstm_gesture_model.h5")
SCALER_PATH = os.path.join(MODELS_DIR, "feature_scaler.pkl")

# --- 关键点与模型参数 ---
NUM_LANDMARKS = 21
LANDMARK_DIM = 2  # x, y
STATIC_FEATURES_COUNT = NUM_LANDMARKS * LANDMARK_DIM
DYNAMIC_FEATURES_COUNT = STATIC_FEATURES_COUNT
MAX_TRAJECTORY_LENGTH = 16  # LSTM 序列长度

# --- 识别阈值与延迟 ---
STATIC_GESTURE_THRESHOLD = 0.7
DYNAMIC_GESTURE_THRESHOLD = 0.7
MIN_DYNAMIC_TRAJECTORY_LENGTH = 8
DYNAMIC_GESTURE_DELAY = 1.0  # 动态手势触发后，禁用持续时间(秒)

# --- 摄像头设置 ---
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480