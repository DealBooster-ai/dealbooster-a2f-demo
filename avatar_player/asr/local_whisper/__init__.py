import whisper, os
import numpy as np
from scipy.io.wavfile import write
import platform
import torch
import speech_recognition as sr
import io
import os
from .. import IASR
from transformers import pipeline


Model = 'tiny'     # Whisper model size (tiny, base, small, medium, large)
English = True      # Use English-only model?
Translate = False   # Translate non-English to English?
SampleRate = 16000  # Stream device recording frequency
BlockSize = 200      # Block size in milliseconds
Threshold = 0.1     # Minimum volume threshold to activate listening
Vocals = [50, 1000] # Frequency range to detect sounds that could be speech
EndBlocks = 10      # Number of blocks to wait before sending to Whisper

class LocalWhisperASR(IASR):

    english : bool

    _input_handler = None

    asr_pipeline = None


    '''
    Parameners:
        model (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large', 'large-v3-turbo', 'turbo')
        english (bool): Use English-only model?
    '''
    def __init__(self, device_id = None, model='base', english = True):
        self.running = True
        self.padding = 0
        self.prevblock = self.buffer = np.zeros((0,1))
        self.fileready = False
        self.recorded = np.zeros((0, 1))
        print("\033[96mLoading Whisper Model..\033[0m", end='', flush=True)

        device = 'cuda'
        self.platform = platform.system().lower()
        if self.platform == "darwin":
            if device == "cuda" or device == "mps":
                self.logger.warning("CUDA is not supported on MacOS and mps does not work. Using CPU instead.")
            device = "cpu"
        else:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        model_root = '~/.cache/whisper'
        model_root = os.path.expanduser(model_root)
        #model_root = "D:/"
        #self.model = whisper.load_model(f'{self.model}{".en" if self.english else ""}').to(device)
        
        if (model != "large" and model != "large-v2" and model!= "large-v3") and english:
            model = model + ".en"
        self.model = whisper.load_model(model, download_root=model_root).to(device)

        self.asr_pipeline = pipeline("automatic-speech-recognition", model="whitemouse84/whisper-base-ru", device='cuda')

        print("\033[90m Done.\033[0m")


    def __preprocess(self, data):
        return np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0
        

    def callback(self, indata, frames, time, status):
        #if status: print(status) # for debugging, prints stream errors.
        if not any(indata):
            print('\033[31m.\033[0m', end='', flush=True) # if no input, prints red dots
            #print("\033[31mNo input or device is muted.\033[0m") #old way
            #self.running = False  # used to terminate if no input
            return
        # A few alternative methods exist for detecting speech.. #indata.max() > Threshold
        #zero_crossing_rate = np.sum(np.abs(np.diff(np.sign(indata)))) / (2 * indata.shape[0]) # threshold 20
        freq = np.argmax(np.abs(np.fft.rfft(indata[:, 0]))) * SampleRate / frames
        if np.sqrt(np.mean(indata**2)) > Threshold and Vocals[0] <= freq <= Vocals[1]:
            print('.', end='', flush=True)
            if self.padding < 1: self.buffer = self.prevblock.copy()
            self.buffer = np.concatenate((self.buffer, indata))
            self.padding = EndBlocks
        else:
            self.padding -= 1
            print('x', end='', flush=True)
            if self.padding > 1:
                self.buffer = np.concatenate((self.buffer, indata))
            elif self.padding < 1 < self.buffer.shape[0] > SampleRate: # if enough silence has passed, write to file.
                self.fileready = True
                write('dictate-tmp.wav', SampleRate, self.buffer) # I'd rather send data to Whisper directly..
                self.recorded = self.buffer.copy()
                self.buffer = np.zeros((0,1))
                #self.running = False
            elif self.padding < 1 < self.buffer.shape[0] < SampleRate: # if recording not long enough, reset buffer.
                self.buffer = np.zeros((0,1))
                print("o", end='', flush=True)
            else:
                self.prevblock = indata.copy() #np.concatenate((self.prevblock[-int(SampleRate/10):], indata)) # SLOW
                print("z", end='', flush=True)

    def process(self):
        if self.fileready:
            print("\n\033[90mTranscribing..\033[0m")
            #result = self.model.transcribe('dictate-tmp.wav',fp16=False,language='en' if English else '',task='translate' if Translate else 'transcribe', initial_prompt="Hello! Hmm... Umm.. How are you? (cough) Nice to see you.")
            result = self.asr_pipeline('dictate-tmp.wav')
            '''b = io.BytesIO()
            write(b, SampleRate, self.recorded)
            audio = sr.AudioData(self.recorded,SampleRate,2).get_raw_data()
            audio_data = self.__preprocess(audio)
            result = self.model.transcribe(b,language='en' if English else '',task='translate' if Translate else 'transcribe',suppress_tokens="")'''
            self.recorded = np.zeros((0,1))
            print(f"\033[1A\033[2K\033[0G{result['text']}")
            #if self.asst.analyze != None: self.asst.analyze(result['text'])
            if self._input_handler != None:
                self._input_handler(result['text'])
            self.fileready = False

    def run(self, input_handler = None, start_talking_handler = None):
        self._input_handler = input_handler
        print("\033[32mListening.. \033[37m(Ctrl+C to Quit)\033[0m")
        import sounddevice as sd
        with sd.InputStream(channels=1, callback=self.callback, blocksize=int(SampleRate * BlockSize / 1000), samplerate=SampleRate):
            while self.running: self.process()

def main():
    try:
        handler = LocalWhisperASR()
        handler.run()
    except (KeyboardInterrupt, SystemExit): pass
    finally:
        print("\n\033[93mQuitting..\033[0m")
        if os.path.exists('dictate-tmp.wav'): os.remove('dictate-tmp.wav')

if __name__ == '__main__':
    main() 