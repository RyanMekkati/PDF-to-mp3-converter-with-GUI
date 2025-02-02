import tkinter as tk
from tkinter import filedialog, scrolledtext
import os
import threading
import time
import pygame
from pdf_utils import extract_text_from_pdf
from audio_utils import text_to_speech, play_audio, pause_audio, stop_audio, set_volume

mp3_files = []  # List to store MP3 file names
pdf_text = None
current_index = 0  # Tracks which paragraph is being read
speed_factor = 1.0
volume_level = 1.0

# Function to process the PDF and display text
def process_pdf():
    global pdf_text, mp3_files, current_index
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not pdf_path:
        status_label.config(text="No PDF selected")
        return

    pdf_text = extract_text_from_pdf(pdf_path)
    if not pdf_text:
        status_label.config(text="PDF has no readable text")
        return

    # Display text in the text area
    text_area.config(state=tk.NORMAL)
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, pdf_text)
    text_area.config(state=tk.DISABLED)

    # Reset paragraph index and MP3 files list
    current_index = 0
    mp3_files.clear()

    # Split text into paragraphs
    paragraphs = pdf_text.split("\n\n")  # Splitting on double newlines (adjust if needed)

    # Start processing first paragraph
    if paragraphs:
        threading.Thread(target=generate_mp3_in_background, args=(paragraphs, 0)).start()
        status_label.config(text="Generating audio...")

# Function to generate MP3 asynchronously
def generate_mp3_in_background(paragraphs, start_index):
    global mp3_files

    for i in range(start_index, len(paragraphs)):
        paragraph = paragraphs[i].strip()
        if not paragraph:
            continue

        pdf_name = f"part_{i+1}.mp3"
        mp3_path = text_to_speech(paragraph, pdf_name)  # Generate MP3 file

        if mp3_path:
            mp3_files.append(mp3_path)  # Store MP3 file path

        # If it's the first paragraph, start playing immediately
        if i == start_index:
            threading.Thread(target=play_next_paragraph).start()

# Function to play MP3 and highlight text
def play_next_paragraph():
    global current_index

    while current_index < len(mp3_files):
        if pygame.mixer.music.get_busy():
            time.sleep(1)  # Wait until the current audio finishes
            continue

        mp3_file = mp3_files[current_index]
        threading.Thread(target=play_audio, args=(mp3_file, speed_factor, volume_level)).start()
        highlight_text(current_index)
        current_index += 1

# Function to highlight the paragraph being read
def highlight_text(index):
    global pdf_text

    paragraphs = pdf_text.split("\n\n")
    if index >= len(paragraphs):
        return

    text_area.config(state=tk.NORMAL)
    text_area.tag_remove("highlight", "1.0", tk.END)

    start = text_area.search(paragraphs[index], "1.0", stopindex=tk.END)
    if start:
        end = f"{start}+{len(paragraphs[index])}c"
        text_area.tag_add("highlight", start, end)
        text_area.tag_config("highlight", background="yellow")

    text_area.config(state=tk.DISABLED)

# Function to update speed
def set_speed(val):
    global speed_factor
    speed_factor = float(val)

# Function to update volume
def set_volume_gui(val):
    global volume_level
    volume_level = float(val)
    set_volume(volume_level)

# GUI setup
root = tk.Tk()
root.title("PDF to Speech")
root.geometry("600x500")

status_label = tk.Label(root, text="Select a PDF to convert", fg="blue")
status_label.pack(pady=10)

load_pdf_button = tk.Button(root, text="Select PDF", command=process_pdf)
load_pdf_button.pack(pady=5)

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15, width=70)
text_area.pack(pady=10)
text_area.config(state=tk.DISABLED)

play_button = tk.Button(root, text="Play", command=lambda: threading.Thread(target=play_next_paragraph).start())
play_button.pack(pady=5)

pause_button = tk.Button(root, text="Pause", command=pause_audio)
pause_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop", command=stop_audio)
stop_button.pack(pady=5)

speed_label = tk.Label(root, text="Speed Control:")
speed_label.pack()
speed_slider = tk.Scale(root, from_=0.5, to=2.0, resolution=0.1, orient="horizontal", command=set_speed)
speed_slider.set(1.0)
speed_slider.pack()

volume_label = tk.Label(root, text="Volume Control:")
volume_label.pack()
volume_slider = tk.Scale(root, from_=0.0, to=1.0, resolution=0.1, orient="horizontal", command=set_volume_gui)
volume_slider.set(1.0)
volume_slider.pack()

root.mainloop()