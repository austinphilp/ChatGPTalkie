from contextlib import redirect_stdout
from io import BytesIO
from time import sleep

from pydub import AudioSegment
from pydub.playback import play

from utils import silence

with redirect_stdout(None):
    from pygame import mixer

    mixer.init()


def play_sound_from_file(file_name):
    with open(file_name, "rb") as file:
        play(AudioSegment.from_file(file, format="mp3"))

    # # TODO - get rid of this method in favor of using pydub
    # mixer.music.load(file_name)
    # mixer.music.play(fade_ms=0)
    # if wait is True:
    #     while mixer.music.get_busy():
    #         sleep(0.25)


def play_sound_from_bytes(bytes):
    audio_data = BytesIO(bytes)
    # Hack to prevent tons of errors from popping up because the audio server on my machine is terribly configured
    with silence():
        play(AudioSegment.from_file(audio_data, format="mp3"))
