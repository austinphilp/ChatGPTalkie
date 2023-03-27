import asyncio
import pyaudio
import math
import struct
import time
import os

from sounds import play_sound_from_file
from utils import silence

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent

SPEAKING_THRESHOLD = 50
PERCUSSIVE_RATIO_THRESHOLD = 800

SHORT_NORMALIZE = 1.0 / 32768.0
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

INITIAL_TIMEOUT_LENGTH = 5
TIMEOUT_LENGTH = 2

RECORDING_START_SOUND_PATH = os.path.join(os.getcwd(), "media/recording-start.mp3")
RECORDING_END_SOUND_PATH = os.path.join(os.getcwd(), "media/recording-end.mp3")


class TranscriptionEventHandler(TranscriptResultStreamHandler):
    def __init__(self, *args, **kwargs):
        self.segments = []
        super().__init__(*args, **kwargs)

    @property
    def result(self):
        return " ".join(self.segments)

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This handler can be implemented to handle transcriptions as needed.
        # In this case, we're simply printing all of the returned results
        results = transcript_event.transcript.results
        for result in results:
            if result.alternatives:
                seg_text = result.alternatives[0].transcript
                if not result.is_partial:
                    self.segments.append(seg_text)
                    print(f">> {self.result}", end="\r", flush=True)
                else:
                    print(f">> {self.result}{seg_text}", end="\r", flush=True)


class Recorder:
    def __init__(self):
        # Hack to prevent tons of errors from popping up because the audio server on my machine is terribly configured
        with silence():
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK,
            )

    def rms(self, frame):
        # Returns the Root Mean Square - which is a rough measure of average loudness within this frame
        count = len(frame) / 2
        format = "%dh" % (count)
        sum_squares = 0.0
        normalized_squares = []
        for sample in struct.unpack(format, frame):
            n = sample * SHORT_NORMALIZE
            normalized_squares.append((n * n))
            sum_squares += n * n
        rms = math.pow(sum_squares / count, 0.5)
        return rms * 1000, normalized_squares

    def has_percussion(self, frame):
        rms, normalized_squares = self.rms(frame)
        # Basically check if the RMS is a sufficiently low ration of the maximum sound frame
        # Essentially, we want mostly quiet with a single loud sound (a finger snap in this case)
        return rms / max(normalized_squares) * 1 < PERCUSSIVE_RATIO_THRESHOLD

    def has_active_speech(self, frame):
        # Checks the average noise level in this frame, if it's over a threshold, return true
        rms, _ = self.rms(frame)
        print(rms)
        return rms >= SPEAKING_THRESHOLD

    async def record(self, stream):
        # Set initial timeout to be longer than usual
        current = time.time()
        end = time.time() + INITIAL_TIMEOUT_LENGTH
        # Keep listening until we've gone the length of the timeout without detecting active speech, sending each chunk as it's
        # recorded to AWS Transcribe
        while current <= end:
            data = self.stream.read(CHUNK)
            current = time.time()
            if self.has_active_speech(data):
                end = current + TIMEOUT_LENGTH
            await stream.input_stream.send_audio_event(audio_chunk=data)
        # Play a chime to denote that the recording is over and wait for transcription to finish
        play_sound_from_file(RECORDING_START_SOUND_PATH)
        await stream.input_stream.end_stream()

    async def listen_for_trigger(self):
        # Listen continuously until percussive noise is detected
        # set initial value past window
        last_percussion = time.time() - 1
        # Listen until you hear two percussive noises in relatively quick succession
        while True:
            if self.has_percussion(self.stream.read(CHUNK)):
                time_elapsed = time.time() - last_percussion
                if 0.2 < time_elapsed < 0.7:
                    play_sound_from_file(RECORDING_END_SOUND_PATH)
                    break
                last_percussion = time.time()

        # Play chime to indicate the start of the recording
        # Initialize the Transcribe streamer
        stream = await TranscribeStreamingClient(region="us-west-2").start_stream_transcription(
            language_code="en-US",
            media_sample_rate_hz=RATE,
            media_encoding="pcm",
        )
        # Instantiate our handler and start processing events
        handler = TranscriptionEventHandler(stream.output_stream)
        # record audio, streamining it straight to AWS for transcription, gathering the results
        await asyncio.gather(self.record(stream), handler.handle_events())
        print(">> recording...", end="\r", flush=True)
        return handler.result


async def record_snippet():
    return await Recorder().listen_for_trigger()
