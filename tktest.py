import tkinter as tk
from tkinter import filedialog

def open_file_dialog():
    filename = filedialog.askopenfilename()
    if filename:
        print("Selected file:", filename)
        # You can save the selected file path or use it directly in your program

root = tk.Tk()
root.withdraw()  # Hide the main window

open_file_dialog()