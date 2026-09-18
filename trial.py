import tkinter as tk
from tkinter import filedialog

# Hide the main root window
root = tk.Tk()
root.withdraw()

# Open the folder selection dialog
folder_path = filedialog.askdirectory(title="Select a Folder")

# Print the chosen path
print("Selected folder:", folder_path)