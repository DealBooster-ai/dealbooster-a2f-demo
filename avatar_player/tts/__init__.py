from abc import abstractmethod
import numpy as np

class TTSInterface:

    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_full_audio(self, text : str) -> np.ndarray:
        """
        Generate Text-to-Speech (TTS) audio in WAV format and convert it to a numpy array of float32 values.
        
        Parameters:
            text (str): The text to be converted to speech.
            
        Returns:
            numpy.ndarray: TTS audio as a numpy array of float32 values.
        """
      
        return None