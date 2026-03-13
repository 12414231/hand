# training/train_dynamic_model_from_npy.py
import os
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from scipy.spatial.distance import euclidean
import sys

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def calculate_dynamic_features(sequence):
    """
    从一个轨迹序列 [ [x1,y1], [x2,y2], ... ] 中提取特征。
    这是一个基础示例，您可以根据需要添加更多特征。
    """
    if len(sequence) < 2:
        return np.zeros(4)  # 如果序列太短，返回零特征

    points = np.array(sequence)

    # 1. 轨迹总长度
    total_distance = sum(euclidean(points[i], points[i + 1]) for i in range(len(points) - 1))

    # 2. 起点与终点的距离
    start_end_dist = euclidean(points[0], points[-1])

    # 3. 平均速度 (假设采样频率固定，可以简化为平均步长)
    avg_speed = total_distance / (len(points) - 1) if len(points) > 1 else 0

    # 4. 包围盒的宽高比
    x_coords = points[:, 0]
    y_coords = points[:, 1]
    width = np.max(x_coords) - np.min(x_coords)
    height = np.max(y_coords) - np.min(y_coords)
    aspect_ratio = width / height if height != 0 else 0

    return np.array([total_distance, start_end_dist, avg_speed, aspect_ratio])


def load_dynamic_data_from_npy(dynamic_dataset_dir):
    """
    从 .npy 文件中加载动态手势数据，并提取特征。
    """
    print(f"正在从目录 '{dynamic_dataset_dir}' 加载动态 .npy 文件...")

    all_features = []
    all_labels = []

    for filename in os.listdir(dynamic_dataset_dir):
        if filename.endswith('.npy'):
            gesture_name = filename[:-4]
            file_path = os.path.join(dynamic_dataset_dir, filename)

            print(f"  加载文件: {filename}")

            try:
                # sequences 是一个包含多个轨迹的列表
                # 例如: [ [[x1,y1], [x2,y2]], [[x1,y1], [x2,y2]] ]
                sequences = np.load(file_path, allow_pickle=True)
            except Exception as e:
                print(f"    错误: 无法加载文件 {file_path}, {e}")
                continue

            print(f"    -> 发现 {len(sequences)} 个轨迹样本")

            for sequence in sequences:
                # 为每个轨迹序列提取特征
                features = calculate_dynamic_features(sequence)
                all_features.append(features)
                all_labels.append(gesture_name)

    if not all_features:
        print("错误: 未在数据目录中找到任何有效的动态数据文件。请先使用数据收集器收集动态数据。")
        return np.array([]), np.array([])

    print(f"动态数据加载完成，总共 {len(all_features)} 个样本。\n")

    return np.array(all_features), np.array(all_labels)


if __name__ == "__main__":
    DATASET_DIR = "D:../training/datasets/dynamic"
    MODEL_SAVE_PATH = "../trained_models/dynamic_model_from_npy.pkl"

    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

    # 加载数据
    X, y = load_dynamic_data_from_npy(DATASET_DIR)

    if len(X) == 0 or len(y) == 0:
        print("无法开始训练，因为没有加载到任何动态数据。")
        exit()

    # 分割数据
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"数据分割完成: 训练集 {len(X_train)} 个, 测试集 {len(X_test)} 个\n")

    # 训练模型
    print("开始训练动态模型...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    print("动态模型训练完成!\n")

    # 评估模型
    print("--- 动态模型评估 ---")
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
    print("动态模型保存成功！\n")