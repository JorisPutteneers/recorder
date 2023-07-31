import os
import time
import imageio
import pyautogui
import tkinter as tk
from tkinter import filedialog
import threading
from tkinter.font import Font
import sys

class ScreenRecorderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Recorder")
        self.root.geometry("390x33")  # Set window size to 390x33 pixels
        self.root.configure(bg="black")

        # Load the custom font with 50% smaller size
        custom_font = Font(family="JetBrainsMono", size=5)

        self.output_folder = ""
        self.interval_minutes = 5
        self.recording_duration = 20.0  # Set recording duration to 20 seconds
        self.stop_recording_flag = threading.Event()  # Use threading Event to signal stop

        # Output Folder and Start Buttons Frame
        self.output_start_frame = tk.Frame(root, bg="black")
        self.output_start_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        self.output_folder_label = tk.Label(self.output_start_frame, text="Output Folder:", fg="white", bg="black", font=custom_font)
        self.output_folder_label.pack(side=tk.LEFT)

        self.output_folder_entry = tk.Entry(self.output_start_frame, width=30, font=custom_font)
        self.output_folder_entry.pack(side=tk.LEFT, padx=5)

        self.output_folder_btn = tk.Button(self.output_start_frame, text="Select Folder", command=self.set_output_folder, fg="white", bg="black", bd=0, font=custom_font)
        self.output_folder_btn.pack(side=tk.LEFT, padx=5)

        self.start_btn = tk.Button(self.output_start_frame, text="Start Recording", command=self.start_recording, fg="white", bg="black", bd=0, font=custom_font)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        # Bind the keyboard shortcut Ctrl+Q to quit the application
        self.root.bind("<Control-q>", self.quit_application)

    def set_output_folder(self):
        base_folder = os.path.expanduser("~/Documents/dezact/TheCityAndTheCity/src/content/dummy_group/dummy_name/dummy_week/research")
        self.output_folder = filedialog.askdirectory(initialdir=base_folder)
        self.output_folder_entry.delete(0, tk.END)
        self.output_folder_entry.insert(0, self.output_folder)

    def start_recording(self):
        if not self.output_folder:
            tk.messagebox.showerror("Error", "Please select an output folder.")
            return

        self.start_btn.config(state=tk.DISABLED)
        self.recording_thread = threading.Thread(target=self.record_screen)
        self.recording_thread.start()

    def record_screen(self):
        while not self.stop_recording_flag.is_set():
            timestamp = time.strftime("%Y%m%d%H%M%S")
            gif_filename = os.path.join(self.output_folder, f"recording_{timestamp}.gif")

            images = []
            start_time = time.time()
            while time.time() - start_time < self.recording_duration and not self.stop_recording_flag.is_set():
                screenshot = pyautogui.screenshot()
                screenshot = screenshot.resize((512, 320))  # Set the output resolution to 512x512 pixels
                images.append(screenshot)
            if not self.stop_recording_flag.is_set():
                imageio.mimsave(gif_filename, images, duration=0.1)

            print(f"Screen recording saved as: {gif_filename}")

            if not self.stop_recording_flag.is_set():
                time.sleep(self.interval_minutes * 60)

        # Re-enable the "Start Recording" button after the recording is complete
        self.root.after(1, self.enable_start_btn)

    def enable_start_btn(self):
        self.start_btn.config(state=tk.NORMAL)

    def quit_application(self, event):
        self.stop_recording_flag.set()  # Set the flag to stop the recording
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="black")
    gui = ScreenRecorderGUI(root)

    # Function to monitor for Ctrl+Q shortcut even while recording
    def monitor_shortcut():
        while True:
            try:
                root.update()
            except tk.TclError:
                # If the root window is destroyed, exit the loop
                break
            if gui.stop_recording_flag.is_set():
                # If the recording has stopped, exit the loop
                break

    # Start the shortcut monitoring thread
    shortcut_thread = threading.Thread(target=monitor_shortcut)
    shortcut_thread.start()

    root.mainloop()