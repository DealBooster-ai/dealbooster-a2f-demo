import numpy as np
from scipy.io.wavfile import write
import platform
import torch
import speech_recognition as sr
from .. import IASR
from transformers import pipeline


SampleRate = 16000
Vocals = [40, 1200] # Frequency range to detect sounds that could be speech
EndBlocks = 8      # Number of blocks to wait before sending to Whisper
BlockSize = 200      # Block size in milliseconds
Threshold = 0.001     # Minimum volume threshold to activate listening

class WhisperHF(IASR):

    english : bool

    _input_handler = None
    _talk_handler = None

    asr_pipeline = None


    '''
    Parameners:
        model (str): hugging face model, like 'openai/whisper-base', 'whitemouse84/whisper-base-ru', etc.
    '''
    def __init__(self, device_id = None, model='openai/whisper-base', prompt=None):
        self.running = True
        self.padding = 0
        self.prompt = prompt
        self.prevblock = self.buffer = np.zeros((0,1))
        self.fileready = False
        self.recorded = np.zeros((0, 1))
        self.device_id = device_id
        print("\033[96mLoading Whisper Model..\033[0m", end='', flush=True)

        device = 'cuda'
        self.platform = platform.system().lower()
        if self.platform == "darwin":
            if device == "cuda" or device == "mps":
                self.logger.warning("CUDA is not supported on MacOS and mps does not work. Using CPU instead.")
            device = "cpu"
        else:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        self.asr_pipeline = pipeline("automatic-speech-recognition", model=model, device=device, initial_prompt=self.prompt)

        print("\033[90m Done.\033[0m")


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
            if self._talk_handler:
                self._talk_handler()
            print('.', end='', flush=True)
            #if self.padding < 1: self.buffer = self.prevblock.copy()
            self.buffer = np.concatenate((self.buffer, indata))
            self.padding = EndBlocks
        else:
            self.padding -= 1
            print('x', end='', flush=True)
            if self.padding > 1:
                self.buffer = np.concatenate((self.buffer, indata))
            elif self.padding < 1 < self.buffer.shape[0] > SampleRate: 
                self.fileready = True
                write('dictate-tmp.wav', SampleRate, self.buffer) 
                self.recorded = self.buffer.copy()
                self.buffer = np.zeros((0,1))
                #self.running = False
            elif self.padding < 1 < self.buffer.shape[0] < SampleRate: 
                self.buffer = np.zeros((0,1))
                print("o", end='', flush=True)
            else:
                self.prevblock = indata # np.concatenate((self.prevblock, indata))[-100000:] 
                print("z", end='', flush=True)

    def process(self):
        if self.fileready:
            print("\n\033[90mTranscribing..\033[0m")
            result = self.asr_pipeline('dictate-tmp.wav', initial_prompt=self.prompt)
            self.recorded = np.zeros((0,1))
            print(f"\033[1A\033[2K\033[0G{result['text']}")
            if self._input_handler != None:
                self._input_handler(result['text'])
            self.fileready = False

    def run(self, input_handler = None, talking_handler = None):
        self._input_handler = input_handler
        self._talk_handler = talking_handler
        print("\033[32mListening.. \033[37m(Ctrl+C to Quit)\033[0m")
        import sounddevice as sd
        with sd.InputStream(channels=1, callback=self.callback, blocksize=int(SampleRate * BlockSize / 1000), samplerate=SampleRate, device=self.device_id):
            while self.running: self.process()



if __name__ == "__main__":

    def handler(text:str):
        print(text)
    asr = WhisperHF(model='whitemouse84/whisper-base-ru')
    #asr = WhisperHF()
    asr.run(handler)