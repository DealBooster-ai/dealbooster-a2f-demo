from numpy import ndarray
from . import TTSInterface
import io
from scipy.io.wavfile import read, write
import numpy as np
from pydub import AudioSegment
import requests
import time
import os
import soundfile as sf

class ElevenLabsMultilingual(TTSInterface):

    VOICE_ID = "EXAVITQu4vr4xnSDxMaL"

    def __init__(self, voice_id = None) -> None:
        if not voice_id is None:
            self.VOICE_ID = voice_id
        super().__init__()

    def get_full_audio(self, text: str) -> ndarray:
        ELEVENLABS_API_KEY = os.environ['ELEVENLABS_API_KEY']
        voice_id = self.VOICE_ID

        CHUNK_SIZE = 4096
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"  
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }

        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "use_speaker_boost": True
            }
        }

        file_dir = os.path.join(os.path.expanduser("~"), "audio")
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        file_path = os.path.join(file_dir, f"output{int(time.time())}.mp3")

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    f.write(chunk)
            print(f"File saved to {file_path}")
            audio_data, samplerate = sf.read(file_path, dtype='float32')
            if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)
            os.remove(file_path)
            return audio_data
        else:
            print("Failed to generate speech. Status code:", response.status_code)
            print("Response:", response.text)
        
        # Mark the task as done

    def sample_rate(self):
        return 44100

        