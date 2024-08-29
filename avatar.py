import io
import os, sys, contextlib
import numpy as np
import speech_recognition as sr
from gtts import gTTS
import requests

from pydub import AudioSegment
from scipy.io.wavfile import read, write

import audio2face_pb2
import audio2face_pb2_grpc

import grpc
from audio2face_streaming_utils import push_audio_track
import pyttsx4

ACTIVE_AT_START = True
BACKEND_HOST = "http://18.156.128.185"

@contextlib.contextmanager
def ignoreStderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)


def ask_backend(request_history):
    
    resp = requests.post(BACKEND_HOST + "/api/chat", json=request_history)

    yield resp.text


def ask_openai(request_history):
    from openai import OpenAI
    """
    Generate and yield complete sentences from the output of the chatbot.

    Parameters:
        p (str): The prompt or input to be given to the chatbot.

    Yields:
        str: Complete sentences obtained from the chatbot's responses.
    """
    openai = OpenAI(
        api_key=os.environ.get('OPEN_AI_KEY')
    )
    messages_history = [{"role": "system", "content": "You are a sales trainig avatar named Mary. A sales representative talk to you. \
                         You play as a customer. Make it tricky for the seales rep, reply with concerns, tricky questions, etc.\
                         Not more then one concern or question per reply. Reply concise and short as it is a fluent dialog. One-or two sentencies."}]
    messages_history = messages_history + request_history
    completion = openai.chat.completions.create(
    model="gpt-4o",
    messages=messages_history
    )
    openai_response = completion.choices[0].message.content
    yield openai_response


# Global speech recognition instance
asr = sr.Recognizer()

def speech_to_text(audio: sr.AudioData):
    """
    Convert speech audio to text using Google Web Speech API.
    
    Parameters:
        audio (sr.AudioData): Speech audio data.
        
    Returns:
        Tuple[bool, Union[str, Type[Exception]]]: A tuple containing a boolean indicating if the recognition
                                                 was successful (True) or not (False), and the recognized text
                                                 or the class of the exception if an error occurred.
    """
    global asr
    try:
        # Use Google Web Speech API to recognize speech from audio data
        return True, asr.recognize_google(audio, language="en-US")
    except Exception as e:
        # If an error occurs during speech recognition, return False and the type of the exception
        return False, e.__class__


def get_tts_data(text: str) -> bytes:
    """
    Generate Text-to-Speech (TTS) audio in mp3 format.
    
    Parameters:
        text (str): The text to be converted to speech.
        
    Returns:
        bytes: TTS audio in mp3 format.
    """
    # Create a BytesIO object to hold the TTS audio data in mp3 format
    tts_result = io.BytesIO()
    # Generate TTS audio using gTTS library with the specified text and language (en-US)
    tts = gTTS(text=text, lang='en-US', slow=False)
    # Write the TTS audio data to the BytesIO object
    tts.write_to_fp(tts_result)
    tts_result.seek(0)
    # Read and return the TTS audio data as bytes
    return tts_result.read()

def tts_to_wav(tts_byte: bytes, framerate: int = 22050) -> np.ndarray:
    """
    Convert TTS audio from mp3 format to WAV format and set the desired frame rate and channels.
    
    Parameters:
        tts_byte (bytes): TTS audio in mp3 format.
        framerate (int, optional): Desired frame rate for the WAV audio. Defaults to 22050.
        
    Returns:
        numpy.ndarray: TTS audio in WAV format as a numpy array of float32 values.
    """
    # Convert the TTS audio bytes in mp3 format to a pydub AudioSegment object
    seg = AudioSegment.from_mp3(io.BytesIO(tts_byte))
    # Set the frame rate and number of channels for the audio
    seg = seg.set_frame_rate(framerate)
    seg = seg.set_channels(1)
    # Create a BytesIO object to hold the WAV audio data
    wavIO = io.BytesIO()
    # Export the AudioSegment as WAV audio to the BytesIO object
    seg.export(wavIO, format="wav")
    # Read the WAV audio data from the BytesIO object using scipy.io.wavfile.read()
    rate, wav = read(io.BytesIO(wavIO.getvalue()))
    return wav

def wav_to_numpy_float32(wav_byte: bytes) -> np.ndarray:
    """
    Convert WAV audio from bytes to a numpy array of float32 values.
    
    Parameters:
        wav_byte (bytes): WAV audio data.
        
    Returns:
        numpy.ndarray: WAV audio as a numpy array of float32 values.
    """
    # Convert the WAV audio bytes to a numpy array of float32 values
    return wav_byte.astype(np.float32, order='C') / 32768.0

tts_engine = pyttsx4.init()
voices = tts_engine.getProperty('voices')
tts_engine.setProperty('voice', voices[1].id)

def get_tts_numpy_audio(text: str) -> np.ndarray:
    """
    Generate Text-to-Speech (TTS) audio in WAV format and convert it to a numpy array of float32 values.
    
    Parameters:
        text (str): The text to be converted to speech.
        
    Returns:
        numpy.ndarray: TTS audio as a numpy array of float32 values.
    """
    # Generate TTS audio in mp3 format from the given text
    #mp3_byte = get_tts_data(text)
    # Convert the TTS audio in mp3 format to WAV format and a numpy array of float32 values
    #wav_byte = tts_to_wav(mp3_byte)

    
    b = io.BytesIO()
    tts_engine.save_to_file(text, b)
    tts_engine.runAndWait()
    b.seek(0)
    bs=b.getvalue()
    
    b=bytes(b'RIFF')+ (len(bs)+38).to_bytes(4, byteorder='little')+b'WAVEfmt\x20\x12\x00\x00' \
                                                                b'\x00\x01\x00\x01\x00' \
                                                                b'\x22\x56\x00\x00\x44\xac\x00\x00' +\
        b'\x02\x00\x10\x00\x00\x00data' +(len(bs)).to_bytes(4, byteorder='little')+bs
    
    b=io.BytesIO(b)
    rate, wav_byte = read(b) #read(io.BytesIO(b.getvalue()))

    return wav_to_numpy_float32(wav_byte)

def make_avatar_speaks(text: str) -> None:
    """
    Make the avatar speak the given text by pushing the audio track to the NVIDIA A2F instance.
    
    Parameters:
        text (str): The text to be spoken by the avatar.
        
    Returns:
        None
    """
    global a2f_url
    global sample_rate
    global a2f_avatar_instance
    # Get the TTS audio in WAV format as a numpy array of float32 values
    tts_audio = get_tts_numpy_audio(text)
    # Push the TTS audio to the NVIDIA A2F instance for the avatar to speak
    push_audio_track(a2f_url, tts_audio, sample_rate, a2f_avatar_instance)
    return


# Define the default audio2face URL and port.
default_url = 'localhost'
default_port = 50051

# Set the audio frame rate for the audio data.
sample_rate = 22050  # Replace '22050' with the desired audio frame rate (samples per second).

# Specify the instance name of the avatar in audio2face service.
a2f_avatar_instance = '/World/audio2face/PlayerStreaming'

# Define a variable for the port (you can change the value as needed).
# For example, if you want to use a different port, modify the value of 'port' accordingly.
port = default_port

# Create the complete audio2face URL by combining the URL and port variables.
a2f_url = f'{default_url}:{port}'

dialog_history = []

active = ACTIVE_AT_START

with ignoreStderr():
    with sr.Microphone() as source:
        asr.adjust_for_ambient_noise(source, duration=3)
        asr.pause_threshold
        while True:
            print('Say something')
            audio=asr.listen(source)
            is_valid_input, _input = speech_to_text(audio)
            if is_valid_input:
                print("User : ", _input)
                if _input == "goodbye Mary":
                    active = False
                    make_avatar_speaks("It was pleasure to talk to you!")
                    dialog_history = []
                if active:  
                    print("User : ", _input)
                    dialog_history.append({"role": "user", "content": _input})
                    for sentence in ask_backend(dialog_history):
                        print("Avatar : ", sentence)
                        dialog_history.append({"role": "assistant", "content": sentence}) 
                        make_avatar_speaks(sentence)
                if active == False and _input == "hello Mary":
                    active = True
                    make_avatar_speaks("Hello! My Name is Donald. You can try to sell something to me.")
                    dialog_history.append({"role": "assistant", "content": "Hello! My Name is Mary. You can try to sell something to me."})

            else:
                if _input is sr.RequestError:
                    print("No response from Google Speech Recognition service: {0}".format(_input))