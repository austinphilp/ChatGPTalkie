#!/usr/bin/python3
import asyncio
import sys

from openai.error import Timeout as OpenAITimeout
from colorama import Fore, Style

from record import record_snippet
from polly import text_to_speech
from chatgpt import OpenAIClient

client = OpenAIClient()


if __name__ == "__main__":
    # TODO - allow a fingersnap to interrupt ChatGPT's playback and start new question
    while True:
        print(Style.BRIGHT + Fore.CYAN + ">> waiting...", end="\r", flush=True)
        # Wait for trigger (two fingernaps) and record a question - the transcription will be done asyncronously while the
        # recording is in progress
        text = asyncio.run(record_snippet())
        text = text.strip()

        if len(text) == 0:
            print(">> failed...     ", end="\r", flush=True)
            text_to_speech("Sorry, I didn't catch that, could you try again?")
            continue
        # TODO - use regex
        elif text.lower().replace(".", "") == "stop":
            print(">> exiting...     ", end="\r", flush=True)
            text_to_speech("Have a nice day")
            sys.exit(0)

        print(f">> {text}", flush=True)
        # TODO - play waiting chime while loading
        print(Style.BRIGHT + Fore.GREEN + ">> Waiting for ChatGPT...", end="\r")
        try:
            resp = client.req(text)
        except OpenAITimeout:
            text_to_speech("Sorry, I had trouble with that one, maybe try rephrasing?")
            continue

        print(f">> {resp}")
        text_to_speech(resp)
