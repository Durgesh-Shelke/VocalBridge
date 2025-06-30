import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import threading
import whisper
import sounddevice as sd
import numpy as np
import wave
import os
from PIL import Image, ImageTk
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Load Aya-101 translation model
local_model_path = "models--CohereForAI--aya-101/snapshots/709e97e4be8ab731f6f81bebd1402db15468b29f"
tokenizer = AutoTokenizer.from_pretrained(local_model_path)
aya_model = AutoModelForSeq2SeqLM.from_pretrained(local_model_path)

class TranslationUIDesign:
    def __init__(self, root):
        self.root = root
        self.root.title("Speak & Translate")
        self.root.geometry("700x650")

        try:
            self.model = whisper.load_model("turbo")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Whisper model:\n{e}")
            self.model = None
            return

        self.recording = False
        self.audio_data = []
        self.samplerate = 44100
        self.audio_counter = 1
        self.transcribed_text = ""
        self.detected_language = ""
        self.selected_language = tk.StringVar(value="English")

        self.canvas = tk.Canvas(self.root, width=700, height=650)
        self.canvas.pack(fill="both", expand=True)

        self.bg_image = Image.open("3425171.jpg")
        self.update_background()
        self.canvas.bind("<Configure>", self.update_background)

        self.widgets = []
        self.create_homepage()

    def update_background(self, event=None):
        width = event.width if event else 700
        height = event.height if event else 650
        resized_image = self.bg_image.resize((width, height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_image)
        self.canvas.delete("bg")
        self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="bg")

    def clear_ui(self):
        self.canvas.delete("ui")
        for widget in self.widgets:
            widget.destroy()
        self.widgets = []

    def create_homepage(self):
        self.clear_ui()
        self.canvas.create_text(350, 50, text="Speak & Translate", font=("Arial", 20), fill="white", tags="ui")
        
        self.language_dropdown = ttk.Combobox(self.root, values=["English", "Spanish", "French", "German", "Chinese"], textvariable=self.selected_language, state="readonly")
        self.canvas.create_window(350, 90, window=self.language_dropdown, tags="ui")
        self.widgets.append(self.language_dropdown)

        buttons = [
            ("Record Audio", self.start_recording, "#00CED1"),
            ("Stop Recording", self.stop_recording, "#FF4500"),
            ("Upload Audio File", self.select_audio_file, "#00BFFF"),
            ("Translate", self.translate_text, "#32CD32")
        ]

        for i, (text, command, bg) in enumerate(buttons):
            btn = tk.Button(self.root, text=text, bg=bg, fg="white", font=("Arial", 12), command=command)
            self.canvas.create_window(350, 140 + i * 60, window=btn, tags="ui")
            self.widgets.append(btn)

        self.language_box = tk.Label(self.root, text="Detected Language: ", font=("Arial", 12, "bold"), bg="white")
        self.canvas.create_window(350, 380, window=self.language_box, tags="ui")
        self.widgets.append(self.language_box)

        self.text_box = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=60, height=10)
        self.canvas.create_window(350, 480, window=self.text_box, tags="ui")
        self.widgets.append(self.text_box)

    def select_audio_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3;*.wav;*.m4a;*.flac")])
        if file_path:
            self.process_audio(file_path)

    def start_recording(self):
        self.recording = True
        self.audio_data = []  # Make sure it's a list
        threading.Thread(target=self.record_audio, daemon=True).start()

    def record_audio(self):
        def callback(indata, frames, time, status):
            # Defensive check to prevent AttributeError
            if self.recording:
                if not isinstance(self.audio_data, list):
                    self.audio_data = []
                self.audio_data.append(indata.copy())

        with sd.InputStream(callback=callback, samplerate=self.samplerate, channels=1, dtype='int16'):
            while self.recording:
                sd.sleep(100)

    def stop_recording(self):
        self.recording = False
        if self.audio_data:
            os.makedirs("recordings", exist_ok=True)
            filename = f"recordings/record_{self.audio_counter}.wav"
            audio_np = np.concatenate(self.audio_data, axis=0)
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.samplerate)
                wf.writeframes(audio_np.tobytes())
            self.audio_counter += 1
            self.process_audio(filename)

    def process_audio(self, file_path):
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, "Processing audio, please wait...\n")
        self.root.update()

        def process():
            try:
                audio = whisper.load_audio(file_path)
                audio = whisper.pad_or_trim(audio)
                mel = whisper.log_mel_spectrogram(audio, n_mels=self.model.dims.n_mels).to(self.model.device)
                _, probs = self.model.detect_language(mel)
                detected_lang = max(probs, key=probs.get)
                self.detected_language = detected_lang.capitalize()
                self.language_box.config(text=f"Detected Language: {self.detected_language}")
                result = self.model.transcribe(file_path)
                self.transcribed_text = result.get("text", "")
                self.text_box.delete("1.0", tk.END)
                self.text_box.insert(tk.END, self.transcribed_text)
            except Exception as e:
                messagebox.showerror("Error", f"Audio processing failed:\n{e}")
        threading.Thread(target=process, daemon=True).start()

    def translate_text(self):
        if not self.transcribed_text:
            messagebox.showerror("Error", "No text available to translate!")
            return
        
        def translate():
            try:
                inputs = tokenizer.encode(f"Translate to {self.selected_language.get()}: {self.transcribed_text}", return_tensors="pt")
                outputs = aya_model.generate(inputs, max_new_tokens=128)
                translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                self.text_box.insert(tk.END, f"\n\nTranslated Text ({self.selected_language.get()}):\n{translated_text}\n")
            except Exception as e:
                messagebox.showerror("Error", f"Translation failed:\n{e}")
        threading.Thread(target=translate, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationUIDesign(root)
    root.mainloop()