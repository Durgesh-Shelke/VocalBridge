import tkinter as tk
from tkinter import ttk, filedialog
import sounddevice as sd
import numpy as np
import threading
import queue
from PIL import Image, ImageTk

class TranslationUISkeleton:
    def __init__(self, root):
        self.root = root
        self.root.title("Speak & Translate")
        self.root.geometry("600x400")

        # Create a Canvas that fills the window
        self.canvas = tk.Canvas(self.root, width=600, height=400)
        self.canvas.pack(fill="both", expand=True)

        # Load the background image
        self.bg_image = Image.open("3425171.jpg")
        self.update_background()  # Set initial background
        self.canvas.bind("<Configure>", self.update_background)  # Update on resize

        # List to keep track of widgets for cleanup
        self.widgets = []

        # Initialize variables for audio
        self.recording = False
        self.playing = False
        self.audio_data = []
        self.amplitude_queue = queue.Queue()

        # Start with the homepage
        self.create_homepage()

    def update_background(self, event=None):
        """Update the background image to match the current window size."""
        if event:
            width = event.width
            height = event.height
        else:
            width, height = 600, 400
        resized_image = self.bg_image.resize((width, height), Image.LANCZOS)  # Use LANCZOS for better quality
        self.bg_photo = ImageTk.PhotoImage(resized_image)
        self.canvas.delete("bg")
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="bg")

    def clear_ui(self):
        """Clear all UI elements but preserve the background."""
        self.canvas.delete("ui")
        for widget in self.widgets:
            widget.destroy()
        self.widgets = []

    # Homepage
    def create_homepage(self):
        self.clear_ui()

        # Title
        self.canvas.create_text(300, 50, text="Speak & Translate", font=("Arial", 20), fill="white", tags="ui")

        # Buttons with specified colors
        buttons = [
            ("Record Audio", self.record_audio_ui, "#00CED1", "white"),  # Teal for audio
            ("Upload Audio File", self.upload_audio_file, "#00BFFF", "white"),  # Bright blue for primary
            ("Enter Text", self.text_input_ui, "#00BFFF", "white")  # Bright blue for primary
        ]
        for i, (text, command, bg, fg) in enumerate(buttons):
            btn = tk.Button(self.root, text=text, command=command, bg=bg, fg=fg, font=("Arial", 12))
            self.canvas.create_window(300, 100 + i * 60, window=btn, tags="ui")
            self.widgets.append(btn)

    # Record Audio Screen
    def record_audio_ui(self):
        self.clear_ui()

        # Instruction text
        self.canvas.create_text(300, 50, text="Recording... Press Stop when done", font=("Arial", 14), fill="white", tags="ui")

        # Buttons with specified colors
        stop_btn = tk.Button(self.root, text="Stop", command=self.stop_recording, bg="white", fg="black", bd=2, relief="solid", font=("Arial", 12))  # White border, black text
        self.canvas.create_window(300, 300, window=stop_btn, tags="ui")
        self.widgets.append(stop_btn)

        cancel_btn = tk.Button(self.root, text="Cancel", command=self.create_homepage, bg="white", fg="black", bd=2, relief="solid", font=("Arial", 12))  # White border, black text
        self.canvas.create_window(300, 360, window=cancel_btn, tags="ui")
        self.widgets.append(cancel_btn)

        # Start audio recording
        self.recording = True
        self.audio_data = []
        threading.Thread(target=self.record_audio, daemon=True).start()

    def record_audio(self):
        fs = 44100  # Sample rate
        with sd.InputStream(samplerate=fs, channels=1, callback=self.audio_callback):
            while self.recording:
                sd.sleep(100)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_data.append(indata.copy())

    def stop_recording(self):
        self.recording = False
        if self.audio_data:
            self.audio_data = np.concatenate(self.audio_data, axis=0)
        self.show_recording_options()

    # Show options after recording
    def show_recording_options(self):
        self.clear_ui()

        # Title
        self.canvas.create_text(300, 50, text="Recording Complete", font=("Arial", 14), fill="white", tags="ui")

        # Buttons with specified colors
        buttons = [
            ("Replay Audio", self.replay_audio, "#00CED1", "white"),  # Teal for audio
            ("Confirm", self.show_transcription, "#00BFFF", "white"),  # Bright blue for primary
            ("Re-record", self.record_audio_ui, "#00CED1", "white"),  # Teal for audio
            ("Cancel", self.create_homepage, "white", "black")  # White border, black text
        ]
        for i, (text, command, bg, fg) in enumerate(buttons):
            if text == "Cancel":
                btn = tk.Button(self.root, text=text, command=command, bg=bg, fg=fg, bd=2, relief="solid", font=("Arial", 12))
            else:
                btn = tk.Button(self.root, text=text, command=command, bg=bg, fg=fg, font=("Arial", 12))
            self.canvas.create_window(300, 100 + i * 60, window=btn, tags="ui")
            self.widgets.append(btn)

    def replay_audio(self):
        if not hasattr(self, 'audio_data') or len(self.audio_data) == 0:
            print("No audio to replay")
            return
        self.playing = True
        threading.Thread(target=self.play_audio, daemon=True).start()

    def play_audio(self):
        fs = 44100
        index = 0
        def callback(outdata, frames, time, status):
            nonlocal index
            if status:
                print(status)
            if not self.playing:
                raise sd.CallbackStop()
            chunk = self.audio_data[index:index + frames]
            if len(chunk) < frames:
                outdata[:len(chunk)] = chunk
                outdata[len(chunk):] = 0
                raise sd.CallbackStop()
            else:
                outdata[:] = chunk
            index += frames

        with sd.OutputStream(samplerate=fs, channels=1, callback=callback):
            while self.playing and index < len(self.audio_data):
                sd.sleep(100)
        self.playing = False

    # Upload Audio File
    def upload_audio_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3;*.ogg;*.flac")])
        if file_path:
            print(f"Selected file: {file_path}")
            self.show_transcription()

    # Text Input Screen
    def text_input_ui(self):
        self.clear_ui()

        self.canvas.create_text(300, 50, text="Enter Text", font=("Arial", 14), fill="white", tags="ui")

        text_entry = tk.Text(self.root, height=5, width=50)
        self.canvas.create_window(300, 150, window=text_entry, tags="ui")
        self.widgets.append(text_entry)

        submit_button = tk.Button(self.root, text="Submit", command=self.show_transcription, 
                                 bg="#00BFFF", fg="white", font=("Arial", 12))
        self.canvas.create_window(300, 250, window=submit_button, tags="ui")
        self.widgets.append(submit_button)

        back_button = tk.Button(self.root, text="Back", command=self.create_homepage, 
                               bg="#9370DB", fg="white", font=("Arial", 12))  # Purple for secondary
        self.canvas.create_window(300, 310, window=back_button, tags="ui")
        self.widgets.append(back_button)

    # Transcription Screen
    def show_transcription(self):
        self.clear_ui()

        self.canvas.create_text(300, 50, text="Detected Language: [Placeholder]", 
                               font=("Arial", 14), fill="white", tags="ui")
        self.canvas.create_text(300, 80, text="Transcription:", font=("Arial", 12), fill="white", tags="ui")

        transcription_text = tk.Text(self.root, height=5, width=50)
        transcription_text.insert(tk.END, "[Transcribed text goes here]")
        self.canvas.create_window(300, 150, window=transcription_text, tags="ui")
        self.widgets.append(transcription_text)

        proceed_button = tk.Button(self.root, text="Proceed", command=self.select_output_language, 
                                  bg="#00BFFF", fg="white", font=("Arial", 12))
        self.canvas.create_window(300, 250, window=proceed_button, tags="ui")
        self.widgets.append(proceed_button)

        back_button = tk.Button(self.root, text="Back", command=self.create_homepage, 
                               bg="#9370DB", fg="white", font=("Arial", 12))  # Purple for secondary
        self.canvas.create_window(300, 310, window=back_button, tags="ui")
        self.widgets.append(back_button)

    # Output Language Selection Screen
    def select_output_language(self):
        self.clear_ui()

        self.canvas.create_text(300, 50, text="Select Output Language", 
                               font=("Arial", 14), fill="white", tags="ui")

        lang_combo = ttk.Combobox(self.root, values=["English", "Spanish", "French", "Chinese", "German"], 
                                 width=30)
        lang_combo.set("English")
        self.canvas.create_window(300, 100, window=lang_combo, tags="ui")
        self.widgets.append(lang_combo)

        translate_button = tk.Button(self.root, text="Translate", command=self.show_output, 
                                    bg="#00BFFF", fg="white", font=("Arial", 12))
        self.canvas.create_window(300, 160, window=translate_button, tags="ui")
        self.widgets.append(translate_button)

        back_button = tk.Button(self.root, text="Back", command=self.show_transcription, 
                               bg="#9370DB", fg="white", font=("Arial", 12))  # Purple for secondary
        self.canvas.create_window(300, 220, window=back_button, tags="ui")
        self.widgets.append(back_button)

    # Output Screen
    def show_output(self):
        self.clear_ui()

        self.canvas.create_text(300, 50, text="Translation:", font=("Arial", 14), fill="white", tags="ui")

        output_text = tk.Text(self.root, height=5, width=50)
        output_text.insert(tk.END, "[Translated text goes here]")
        self.canvas.create_window(300, 150, window=output_text, tags="ui")
        self.widgets.append(output_text)

        download_button = tk.Button(self.root, text="Download Text", 
                                   command=lambda: print("Download text placeholder"), 
                                   bg="#00BFFF", fg="white", font=("Arial", 12))
        self.canvas.create_window(300, 250, window=download_button, tags="ui")
        self.widgets.append(download_button)

        start_over_button = tk.Button(self.root, text="Start Over", command=self.create_homepage, 
                                     bg="#9370DB", fg="white", font=("Arial", 12))  # Purple for secondary
        self.canvas.create_window(300, 310, window=start_over_button, tags="ui")
        self.widgets.append(start_over_button)

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationUISkeleton(root)
    root.mainloop()