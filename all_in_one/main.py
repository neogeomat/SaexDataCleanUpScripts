import tkinter as tk
from ui import DataCleanup

if __name__ == "__main__":
    root = tk.Tk()
    app = DataCleanup(root)
    root.mainloop()


# pyinstaller --onefile main.py
