import pickle
import os

def load_static_model(model_path):
    """
    加载静态手势识别模型。

    Args:
        model_path (str): 模型文件的路径。

    Returns:
        object: 加载的模型对象，如果失败则返回 None。
    """
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        return None

    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        print(f"成功加载模型: {model_path}")
        return model
    except Exception as e:
        print(f"加载模型时发生错误: {e}")
        return None