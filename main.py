from moviepy.editor import VideoFileClip, CompositeVideoClip
import whisper
from moviepy.video.fx.resize import resize
import cv2
import os

import moviepy.config as mpy_conf 
mpy_conf.change_settings({"FFMPEG_BINARY": os.path.join(os.getcwd(), "ffmpeg.exe")})

#GUI
import customtkinter as ctk
from tkinter import filedialog
import tkinter.filedialog as fd
import threading


ctk.set_appearance_mode("Dark")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VideoSplitter")
        self.geometry("550x370")
        self.iconbitmap("icon.ico")

        self.video_path = None
        self.save_path = None


        self.label = ctk.CTkLabel(self, text="Выберите видео для обработки")
        self.label.pack(pady=5)
        self.select_button = ctk.CTkButton(self, text="Выбрать видео", command=self.select_start_video, text_color="#eeebf7", corner_radius=28, fg_color="#e85c97", hover_color="#d51292")
        self.select_button.pack(pady=8)


        self.label_2 = ctk.CTkLabel(self, text="Выберите папку, в которую будут сохраняться клипы")
        self.label_2.pack(pady=8)
        self.folder_button = ctk.CTkButton(self, text="Выбрать папку", command=self.select_folder_to_save_clips, text_color="#eeebf7", fg_color="#e85c97", corner_radius=28, hover_color="#d51292")
        self.folder_button.pack(pady=8)


        self.process_button = ctk.CTkButton(self, text="Начать обработку", command=self.start_processing, text_color="#eeebf7", fg_color="#e85c97", corner_radius=28, hover_color="#d51292")
        self.process_button.pack(pady=50)

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(pady=1)

        self.status_label_2 = ctk.CTkLabel(self, text="")
        self.status_label_2.pack(pady=1)

        self.mytext = ctk.CTkLabel(self, text="by aqvilov", font=("Arial", 10), text_color="#e85c97")
        self.mytext.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)


    def select_start_video(self):
        self.video_path = fd.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.mkv")])
        if self.video_path:
            self.status_label_2.configure(text=f"Выбрано видео: {os.path.basename(self.video_path)}")

    def select_folder_to_save_clips(self):
        self.save_path = fd.askdirectory()
        if self.save_path:
            self.status_label.configure(text=f"Папка выбрана")

    def start_processing(self):
        thread = threading.Thread(target=self.process_video)
        thread.start()
#gui end

    def process_video(self):
        model = whisper.load_model('base')

        result = model.transcribe(self.video_path, language="ru")

        segments = result["segments"]

        clips = []
        current_start = None
        current_end = None

        for seg in segments:
            if current_start is None:
                current_start = seg['start']
                current_end = seg['end']
            elif seg['end'] - current_start <= 120:
                current_end = seg['end']
            else:
                clips.append((current_start, current_end))
                current_start = seg['start']
                current_end = seg['end']

        if current_start is not None and current_end is not None:
            clips.append((current_start, current_end))


        full_video = VideoFileClip(self.video_path)

        def blur_frame(frame):
            return cv2.GaussianBlur(frame, (63, 63), 30)

        for i, (start, end) in enumerate(clips):
            subclip = full_video.subclip(start, end)

            background = (
                subclip
                .resize(width=720, height=1280)
                .fl_image(blur_frame)

            )

            foreground = (
                subclip
                .resize(0.9)
                .set_position("center")
            )

            overlay_clips = CompositeVideoClip(
                [background, foreground],
                size=(720,1280)
            )

            output = os.path.join(self.save_path, f"clip_{i + 1}.mp4")
            overlay_clips.write_videofile(output)


if __name__ == "__main__":
    app = App()
    app.mainloop()