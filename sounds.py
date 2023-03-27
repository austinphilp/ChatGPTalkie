from io import BytesIO

from pydub import AudioSegment
from pydub.playback import play

from utils import silence


def play_sound_from_file(file_name):
    with open(file_name, "rb") as file:
        play(AudioSegment.from_file(file, format="mp3"))


def play_sound_from_bytes(bytes):
    audio_data = BytesIO(bytes)
    # Hack to prevent tons of errors from popping up because the audio server on my machine is terribly configured
    with silence():
        play(AudioSegment.from_file(audio_data, format="mp3"))
