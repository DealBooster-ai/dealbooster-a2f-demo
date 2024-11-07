from numpy import ndarray
from . import TTSInterface
import io
from scipy.io.wavfile import read, write
import numpy as np
from pydub import AudioSegment
import requests
import json
import os

class ElevenLabs(TTSInterface):

    VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

    def __init__(self, voice_id = None) -> None:
        if not voice_id is None:
            self.VOICE_ID = voice_id
        super().__init__()

    def get_full_audio(self, text: str) -> ndarray:
        """
        Generate Text-to-Speech (TTS) audio in WAV format and convert it to a numpy array of float32 values.
        
        Parameters:
            text (str): The text to be converted to speech.
            
        Returns:
            numpy.ndarray: TTS audio as a numpy array of float32 values.
        """

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

        
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.VOICE_ID}"

        headers = {
            "Content-Type": "application/json",
            "xi-api-key": os.environ.get('ELEVENLABS_API_KEY')
        }

        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            },
            "output_format": "mp3_22050_32"
        }

        response = requests.post(url, json=data, headers=headers)
        audio_bytes = io.BytesIO(response.content)
        audio_segment = AudioSegment.from_mp3(audio_bytes)
        audio_segment = audio_segment.set_frame_rate(22050)
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)
        try:
            rate, wav_byte = read(wav_io)
        except Exception as e:
            print(e)

        return wav_to_numpy_float32(wav_byte)