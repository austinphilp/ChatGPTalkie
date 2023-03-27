# ChatGPTalkie

A simple program for interacting with chatGPT via voice. Simply start the program then snap your fingers twice to wake it and
begin speaking your prompt. 


### Prequisites

Python prerequisites are defined by the pyproject.toml and can be installed into a virtual environment using `poetry install`

In addition you will need an [OpenAI API Key](https://platform.openai.com/account/api-keys), and an AWS account, configured on
your current machine to work with boto3.

Consider yourself warned - use of this program **will incur charges on your OpenAI and AWS Accounts**. It utilize the chat
completion api on chatGPT as well as AWS Transcribe and AWS Polly. None are particularly expensive.


### Installation

If you want to use this program often, you may find it useful to add this program onto your `$PATH` via a symlink

```
ln -s /path/to/main.py /path/to/your/bin
```

### Usage

Usage is quite straightforward, simply run the script, either via your symlink setup above, or directly (`./main.py`).

Once the program is started you'll see a simple prompt `>> waiting` this means the program is currently waiting for it's wake
signal. To wake - simply snap your fingers twice, if the program does not wake you may need to snap louder or move your hand
closer to the mic (I'm still dialing in the thresholds for this). As you talk, you'll see a live transcription of what you say
appear in your terminal.

Once you finish speaking, you'll hear a chime denoting that the mic is turned off and chatGPT will begin processing your
prompt. After a short delay, you should hear it's answer. You can converse back and forth like this indefinitely, though each
round of conversation requires you to snap your fingers again to instigate.
