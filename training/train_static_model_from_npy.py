# training/train_static_model_from_npy.py
import os
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import sys

# 将项目根目录添加到Python路径，方便导入其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# --- 特征提取逻辑 (必须与预测时一致) ---
def extract_features_from_landmarks(landmarks_array):
    """
    从一个包含21个关键点 [x,y,z,x,y,z...] 的数组中提取特征。
    这里直接返回原始坐标作为特征。
    """
    return np.array(landmarks_array).reshape(1, -1)


def load_static_data_from_npy(static_dataset_dir):
    """
    从 .npy 文件中加载静态手势数据。
    """
    print(f"正在从目录 '{static_dataset_dir}' 加载 .npy 文件...")

    all_features = []
    all_labels = []

    for filename in os.listdir(static_dataset_dir):
        if filename.endswith('.npy'):
            gesture_name = filename[:-4]
            file_path = os.path.join(static_dataset_dir, filename)

            print(f"  加载文件: {filename}")

            try:
                samples = np.load(file_path, allow_pickle=True)
            except Exception as e:
                print(f"    错误: 无法加载文件 {file_path}, {e}")
                continue

            print(f"    -> 发现 {len(samples)} 个样本")

            for sample in samples:
                # 确保样本是一维的63维向量
                if sample.shape == (21, 3):
                    sample = sample.flatten()

                features = extract_features_from_landmarks(sample)
                all_features.append(features.flatten())
                all_labels.append(gesture_name)

    if not all_features:
        print("错误: 未在数据目录中找到任何有效的数据文件。请先使用数据收集器收集数据。")
        return np.array([]), np.array([])

    print(f"数据加载完成，总共 {len(all_features)} 个样本。\n")

    return np.array(all_features), np.array(all_labels)


if __name__ == "__main__":
    DATASET_DIR = "D:/xiangmu/hand/training/datasets/static"
    MODEL_SAVE_PATH = "../trained_models/static_model_from_npy.pkl"

    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

    # 加载数据
    X, y = load_static_data_from_npy(DATASET_DIR)

    if len(X) == 0 or len(y) == 0:
        print("无法开始训练，因为没有加载到任何数据。")
        exit()

    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"数据分割完成: 训练集 {len(X_train)} 个, 测试集 {len(X_test)} 个\n")

    # 训练模型
    print("开始训练模型...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    print("模型训练完成!\n")

    # 评估模型
    print("--- 模型评估 ---")
    train_accuracy = clf.score(X_train, y_train)
    test_accuracy = clf.score(X_test, y_test)
    print(f"训练集准确率: {train_accuracy:.4f}")
    print(f"测试集准确率: {test_accuracy:.4f}\n")

    y_pred = clf.predict(X_test)
    print("分类报告 (Test Set):")
    print(classification_report(y_test, y_pred))

    # 保存模型
    print(f"正在将模型保存至: {MODEL_SAVE_PATH}")
    with open(MODEL_SAVE_PATH, 'wb') as f:
        pickle.dump(clf, f)
    print("模型保存成功！\n")