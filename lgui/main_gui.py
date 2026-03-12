import tkinter as tk
from lgui.camera_widget import CameraWidget


class MainGUI:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Gesture AI OS")

        self.video = tk.Label(self.root)
        self.video.pack()

        self.camera = CameraWidget(self.root, self.video)

        self.camera.update()

        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.root.mainloop()

    def close(self):

        self.camera.stop()
        self.root.destroy()