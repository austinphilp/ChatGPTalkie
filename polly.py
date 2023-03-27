import boto3

from sounds import play_sound_from_bytes


OUTPUT_AUDIO_FORMAT = "mp3"


def sanitize_text(text):
    # Escape any reserved character so that they don't conflict with the SSML
    return text.replace("&", "&amp;").replace('"', "&quot;").replace("'", "&apos;").replace("<", "&lt;").replace(">", "&gt;")


def text_to_speech(text, voice_id="Matthew", output="output.mp3"):
    text = sanitize_text(text)
    # Add a pause to start to improve playback
    ssml_text = f'<speak><break strength="strong"/>{text}</speak>'
    # Invoke the Polly service to convert the text to speech.
    # TODO - if the text is large - chunk it and send in pieces, queing up the stream
    response = boto3.client("polly").synthesize_speech(
        Engine="neural",
        Text=ssml_text,
        TextType="ssml",
        VoiceId=voice_id,
        OutputFormat=OUTPUT_AUDIO_FORMAT,
    )
    play_sound_from_bytes(response["AudioStream"].read())
