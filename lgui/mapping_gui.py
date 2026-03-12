import tkinter as tk
from tkinter import ttk
import json
import os

CONFIG_PATH = "config/gesture_mapping.json"


class MappingGUI:

    def __init__(self):

        self.root = tk.Tk()
        self.root.title("Gesture Mapping")

        self.mapping = self.load_mapping()

        self.create_ui()

        self.refresh_list()

        self.root.mainloop()

    # ------------------------
    # UI
    # ------------------------

    def create_ui(self):

        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        tk.Label(frame, text="Gesture").grid(row=0, column=0)
        tk.Label(frame, text="Action").grid(row=0, column=1)

        self.gesture_entry = tk.Entry(frame)
        self.gesture_entry.grid(row=1, column=0)

        self.action_entry = tk.Entry(frame)
        self.action_entry.grid(row=1, column=1)

        tk.Button(
            frame,
            text="Add Mapping",
            command=self.add_mapping
        ).grid(row=1, column=2)

        # List

        self.tree = ttk.Treeview(
            self.root,
            columns=("gesture", "action"),
            show="headings"
        )

        self.tree.heading("gesture", text="Gesture")
        self.tree.heading("action", text="Action")

        self.tree.pack(padx=10, pady=10)

        # Buttons

        btn_frame = tk.Frame(self.root)
        btn_frame.pack()

        tk.Button(
            btn_frame,
            text="Delete",
            command=self.delete_mapping
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Save",
            command=self.save_mapping
        ).pack(side="left", padx=5)

    # ------------------------
    # Data
    # ------------------------

    def load_mapping(self):

        if not os.path.exists(CONFIG_PATH):
            return {}

        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    def save_mapping(self):

        os.makedirs("config", exist_ok=True)

        with open(CONFIG_PATH, "w") as f:
            json.dump(self.mapping, f, indent=4)

        print("Mapping saved")

    # ------------------------
    # List
    # ------------------------

    def refresh_list(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        for gesture, action in self.mapping.items():

            self.tree.insert(
                "",
                "end",
                values=(gesture, action)
            )

    # ------------------------
    # Actions
    # ------------------------

    def add_mapping(self):

        gesture = self.gesture_entry.get()
        action = self.action_entry.get()

        if gesture == "" or action == "":
            return

        self.mapping[gesture] = action

        self.refresh_list()

        self.gesture_entry.delete(0, tk.END)
        self.action_entry.delete(0, tk.END)

    def delete_mapping(self):

        selected = self.tree.selection()

        if not selected:
            return

        item = self.tree.item(selected[0])

        gesture = item["values"][0]

        if gesture in self.mapping:
            del self.mapping[gesture]

        self.refresh_list()


if __name__ == "__main__":
    MappingGUI()