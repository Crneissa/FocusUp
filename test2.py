import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from gtts import gTTS
from moviepy.editor import *
import PySimpleGUI as sg

# ========== CONFIGURATION ==========
IMG_FOLDER = "slides"
AUDIO_FOLDER = "audio"
VIDEO_OUTPUT = "final_presentation.mp4"
SLIDE_DURATION = 5  # seconds per slide

# Create output folders
os.makedirs(IMG_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

def extract_images(pdf_path, output_folder):
    slides = convert_from_path(pdf_path)
    slide_files = []
    for i, slide in enumerate(slides):
        slide_file = os.path.join(output_folder, f"slide_{i}.png")
        slide.save(slide_file, "PNG")
        slide_files.append(slide_file)
    return slide_files

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    return [page.get_text("text") for page in doc]

def text_to_speech(text, output_file):
    tts = gTTS(text=text, lang="en")
    tts.save(output_file)

def create_video(slides, audios, output_file, duration):
    clips = []
    for slide, audio in zip(slides, audios):
        img = ImageClip(slide).set_duration(duration)
        audio_clip = AudioFileClip(audio)
        img = img.set_audio(audio_clip)
        clips.append(img)
    final_video = concatenate_videoclips(clips, method="compose")
    final_video.write_videofile(output_file, fps=24)

def process_pdf(pdf_path):
    if not pdf_path:
        return "No file selected"
   
    slide_files = extract_images(pdf_path, IMG_FOLDER)
    pdf_texts = extract_text(pdf_path)
   
    audio_files = []
    for i, text in enumerate(pdf_texts):
        audio_file = os.path.join(AUDIO_FOLDER, f"slide_{i}.mp3")
        text_to_speech(text, audio_file)
        audio_files.append(audio_file)
   
    create_video(slide_files, audio_files, VIDEO_OUTPUT, SLIDE_DURATION)
    return "✅ Video created successfully: final_presentation.mp4"

# ========== GUI SETUP ==========
layout = [
    [sg.Text("Select a PDF to Convert to Video")],
    [sg.Input(), sg.FileBrowse(file_types=(('PDF Files', '*.pdf'),))],
    [sg.Button("Convert"), sg.Button("Exit")],
    [sg.Text("", size=(40,1), key="-OUTPUT-")]
]

window = sg.Window("PDF to Video Converter", layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == "Exit":
        break
    if event == "Convert":
        result = process_pdf(values[0])
        window["-OUTPUT-"].update(result)

window.close()