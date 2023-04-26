# Note: you need to be using OpenAI Python v0.27.0 for the code below to work
import openai
import ffmpeg
import os
import moviepy.editor as mp
from dotenv import load_dotenv
audio = mp.VideoFileClip("test.mp4").audio
audio.write_audiofile("audio.mp3")

audio_file= open("audio.mp3", "rb")
key = os.getenv('OPENAI_KEY')
print(key)
# openai.api_key = key
# transcript = openai.Audio.transcribe("whisper-1", audio_file)

# print(transcript)