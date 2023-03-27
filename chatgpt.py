#!/usr/bin/python3.10

from os import getenv
import logging

import openai

openai.api_key = getenv("OPENAPI_KEY")
logger = logging.getLogger(__name__)


class OpenAIClient(object):
    _default_chat_model = "gpt-3.5-turbo"
    # _default_chat_model = "gpt-4"

    def __init__(self):
        self._session_tokens = 0
        self._history = [
            {
                "role": "system",
                "content": "Do not mention being an AI language model. I will be interacting with you through text-to-speech, so please keep your responses human-like and conversational",
            }
        ]

    def _base_chat(self, messages, **options):
        res = openai.ChatCompletion.create(
            model=options.get("model", self._default_chat_model),
            messages=messages,
            timeout=30.00,
        )
        self._history = messages
        if res.usage.total_tokens > 3500:
            # Pop from index 1 to keep system messages
            self._history.pop(1)
        return [c.message.content for c in res.choices]

    def req(self, message: str):
        messages = [*self._history, {"role": "user", "content": message}]
        return self._base_chat(messages)[0]
