from gtts import gTTS
from pydub import AudioSegment
import pygame
import os

pygame.mixer.init()

# Default global variables
paused = False
volume_level = 1.0  # 100% volume
speed_factor = 1.0  # Normal speed

def text_to_speech(text, output_file):
    """Converts text to speech and saves it as an MP3 file."""
    try:
        if not text:
            print("No text to convert.")
            return None
        tts = gTTS(text=text, lang="en")
        tts.save(output_file)
        return output_file
    except Exception as e:
        print(f"Error converting text to speech: {e}")
        return None

def change_speed(mp3_file, speed_factor):
    """Modify the playback speed of an MP3 file dynamically."""
    sound = AudioSegment.from_file(mp3_file)
    new_speed = sound._spawn(sound.raw_data, overrides={"frame_rate": int(sound.frame_rate * speed_factor)})
    new_speed = new_speed.set_frame_rate(44100)  # Maintain quality
    new_mp3 = "output_speed.mp3"
    new_speed.export(new_mp3, format="mp3")
    return new_mp3

def play_audio(mp3_file, speed=1.0, volume=1.0):
    """Plays the MP3 file with adjustable speed and volume."""
    global paused, volume_level, speed_factor
    volume_level = volume
    speed_factor = speed

    if mp3_file and os.path.exists(mp3_file):
        if paused:
            pygame.mixer.music.unpause()
            paused = False
        else:
            adjusted_file = change_speed(mp3_file, speed_factor)
            pygame.mixer.music.load(adjusted_file)
            pygame.mixer.music.set_volume(volume_level)
            pygame.mixer.music.play()

def pause_audio():
    """Pauses the currently playing audio."""
    global paused
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        paused = True

def stop_audio():
    """Stops the audio playback."""
    pygame.mixer.music.stop()

def set_volume(volume):
    """Adjusts the audio volume."""
    global volume_level
    volume_level = float(volume)
    pygame.mixer.music.set_volume(volume_level)