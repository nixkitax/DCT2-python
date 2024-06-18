import tkinter as tk
import sv_ttk
from ui_setup import setup_ui

root = tk.Tk()
sv_ttk.set_theme("dark")

setup_ui(root)

root.mainloop()
