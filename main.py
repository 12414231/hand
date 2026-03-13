# main.py
import sys
from PyQt5.QtWidgets import QApplication
from linference.gesture_engine import GestureEngine
from lmodel.predictor import StaticGesturePredictor, DynamicGesturePredictor # 修改导入
from laction.action_executor import ActionExecutor
from lgui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    # 加载模型
    static_model_path = "trained_models/static_model_from_npy.pkl"
    dynamic_model_path = "trained_models/dynamic_model_from_npy.pkl"

    static_predictor = StaticGesturePredictor(static_model_path) # 修改类名
    dynamic_predictor = DynamicGesturePredictor(dynamic_model_path) # 修改类名

    # 创建动作执行器
    action_executor = ActionExecutor()

    # 创建手势引擎，并传入预测器和动作执行器
    gesture_engine = GestureEngine(
        static_predictor=static_predictor,
        dynamic_predictor=dynamic_predictor,
        action_executor=action_executor
    )

    # 创建主窗口，传入手势引擎
    window = MainWindow(gesture_engine)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()