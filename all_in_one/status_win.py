import tkinter as tk
class YourClassName:
    def __init__(self, master):
        self.master = master
        self.status_window = None
        self.status_label = None
        # Other initialization code...

    def create_status_window(self):
        """Create the Toplevel window for status updates."""
        self.status_window = tk.Toplevel(self.master)
        self.status_window.title("Status Update")
        self.status_window.geometry("400x200")
        self.status_label = tk.Label(self.status_window, text="", wraplength=380, justify=tk.LEFT)
        self.status_label.pack(padx=10, pady=10)
        self.status_window.transient(self.master)
        self.status_window.grab_set()  # Prevent interaction with the main window

    def update_status(self, message):
        """Update the status label in the Toplevel window."""
        if self.status_window is None or not self.status_window.winfo_exists():
            self.create_status_window()

        self.status_label.config(text=message)
        self.status_window.update_idletasks()

    def close_status_window(self):
        """Close the Toplevel status window when the process is complete."""
        if self.status_window and self.status_window.winfo_exists():
            self.status_window.destroy()
        self.status_window = None
