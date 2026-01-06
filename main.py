from tkinter import *
import tkinter as tk
from tkinter import messagebox
import text_editor as te
import os


current_directory = os.getcwd()
folder_path = current_directory + "/PyProjects"

try:
    os.makedirs(folder_path, exist_ok=True)
    print(f"Director '{folder_path}' ensured to exist.")
except OSError as e:
    messagebox.showerror("Fatal Error", "The folder path has not been found. File operation functionality won't work.", parent=root)

root = Tk()
root.title("PyEditor")
root.geometry("800x500")

top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X)
# buttons for file ops
open_button = tk.Button(top_frame, text="Open", command=lambda: te.on_open_click(editor))
open_button.pack(side=tk.LEFT, padx=5, pady=5)
save_button = tk.Button(top_frame, text="Save As", command=lambda: te.on_save_as_click(editor))
save_button.pack(side=tk.LEFT, padx=5, pady=5)
run_button = tk.Button(top_frame, text="Run", command=lambda: te.on_run_click(editor))
run_button.pack(side=tk.LEFT, padx=5, pady=5)
editor = te.TextEditor(root)

root.mainloop()
