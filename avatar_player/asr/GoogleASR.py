import os, sys, contextlib
import speech_recognition as sr
import contextlib
from . import IASR


class GoogleASR(IASR):

    def __init__(self, device_id = None) -> None:
        pass


    def run(self, input_handler, start_talking_handler = None):
        self.asr = sr.Recognizer()

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
            try:
                # Use Google Web Speech API to recognize speech from audio data
                return True, self.asr.recognize_google(audio, language="en-US")
            except Exception as e:
                # If an error occurs during speech recognition, return False and the type of the exception
                return False, e.__class__

        with ignoreStderr():
            with sr.Microphone() as source:
                self.asr.adjust_for_ambient_noise(source, duration=3)
                #self.asr.pause_threshold
                while True:
                    print('Say something')
                    audio=self.asr.listen(source)
                    is_valid_input, _input = speech_to_text(audio)
                    if is_valid_input:
                        input_handler(_input)

                    else:
                        if _input is sr.RequestError:
                            print("No response from Google Speech Recognition service: {0}".format(_input))