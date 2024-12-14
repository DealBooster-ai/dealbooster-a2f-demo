from numpy import ndarray
import pyttsx4
from . import TTSInterface
import io
from scipy.io.wavfile import read, write
import numpy as np

class PYTTSx4(TTSInterface):

    tts_engine: any

    voice_index: int

    def __init__(self, voice_index = 0) -> None:
        self.voice_index = voice_index
        self.tts_engine = pyttsx4.init()
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

        
        b = io.BytesIO()
        voices = self.tts_engine.getProperty('voices')
        self.tts_engine.setProperty('voice', voices[self.voice_index].id)
        self.tts_engine.save_to_file(text, b)
        self.tts_engine.runAndWait()
        b.seek(0)
        bs=b.getvalue()
        
        b=bytes(b'RIFF')+ (len(bs)+38).to_bytes(4, byteorder='little')+b'WAVEfmt\x20\x12\x00\x00' \
                                                                    b'\x00\x01\x00\x01\x00' \
                                                                    b'\x22\x56\x00\x00\x44\xac\x00\x00' +\
            b'\x02\x00\x10\x00\x00\x00data' +(len(bs)).to_bytes(4, byteorder='little')+bs
        
        b=io.BytesIO(b)
        rate, wav_byte = read(b) 
        return wav_to_numpy_float32(wav_byte)
    

    def sample_rate(self):
        return 22050