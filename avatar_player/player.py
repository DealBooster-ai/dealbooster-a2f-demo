import os, sys, contextlib
import speech_recognition as sr
import contextlib
from .omniverse_client.audio2face_streaming_utils import push_audio_track, push_audio_track_stream
from .tts import TTSInterface
from .avatar_brains import IAvatarBrians
from avatar_player.emotion_changer import EmotionChanger
from .asr import IASR
import queue

import threading
import numpy as np
import requests
import time



class AvatarPlayer:

    active: bool = True
    activation_phrase: str
    deactivation_phrase: str
    hello_message: str
    goodbye_message: str

    audio_tasks_queue = queue.Queue()
    send_to_atf_queue = queue.Queue()
    emotions_queue = queue.Queue()

    def __init__(self, brain:IAvatarBrians, tts_engine:TTSInterface, asr:IASR,
                 emotion_changer:EmotionChanger = None,                 
                 a2f_sample_rate: int =  22050,
                 a2f_host: str = "localhost", a2f_grpc_port:int = 50051,
                 a2f_player_instance: str = '/World/audio2face/PlayerStreaming',
                 activation_phrase = "start experience", deactivation_phrase = "end experience",
                 hello_message = "Hello!", goodbye_message = "Goodbye!", sentence_chunking: bool = True) -> None:
        self.tts_engine = tts_engine
        self.brain = brain
        self.asr = asr
        self.sentence_chunking = sentence_chunking
        self.emotion_changer = emotion_changer #EmotionChanger(a2f_host=a2f_host) if emotion_changer is None else emotion_changer
        self.activation_phrase = activation_phrase
        self.deactivation_phrase = deactivation_phrase
        self.hello_message = hello_message
        self.goodbye_message = goodbye_message
        self.a2f_sample_rate = a2f_sample_rate
        self.a2f_player_instance = a2f_player_instance
        self.a2f_grpc_url = f'{a2f_host}:{a2f_grpc_port}'
        if emotion_changer is None:
            self.emotion_changer = EmotionChanger()


        def text_que():
            while True:
                message = self.audio_tasks_queue.get()
                text = message.get('text')
                audio_data = self.tts_engine.get_full_audio(text)
                self.send_to_atf_queue.put({'audio': audio_data, 'emotion': message.get('emotion')})
                self.audio_tasks_queue.task_done()

        def send_to_atf_worker():
            while True:
                a2f_que = self.send_to_atf_queue.get()
                audio_data = a2f_que.get('audio')
                push_audio_track_stream(self.a2f_grpc_url, audio_data, self.tts_engine.sample_rate(), self.a2f_player_instance)
                self.emotions_queue.put(a2f_que.get('emotion'))
                self.send_to_atf_queue.task_done()

        def send_emotion():
            while True:
                emotion = self.emotions_queue.get()
                self.emotion_changer.change_emotion(emotion)
                self.emotions_queue.task_done()

        audio_worker_thread = threading.Thread(target=text_que)
        audio_worker_thread.daemon = True  
        audio_worker_thread.start()

        atf_worker_thread = threading.Thread(target=send_to_atf_worker)
        atf_worker_thread.daemon = True
        atf_worker_thread.start()

        emotion_worker_thread = threading.Thread(target=send_emotion)
        emotion_worker_thread.daemon = True
        emotion_worker_thread.start()
        pass


    def make_avatar_speaks(self, text: str) -> None:
        """
        Make the avatar speak the given text by pushing the audio track to the NVIDIA A2F instance.
        
        Parameters:
            text (str): The text to be spoken by the avatar.
            
        Returns:
            None
        """
        # Get the TTS audio in WAV format as a numpy array of float32 values
        tts_audio = self.tts_engine.get_full_audio(text)
        # Push the TTS audio to the NVIDIA A2F instance for the avatar to speak
        push_audio_track(self.a2f_grpc_url, tts_audio, self.a2f_sample_rate, self.a2f_player_instance)
        return
    
   
    
    def _handle_asr_input(self, _input:str):
        if _input == self.deactivation_phrase:
            self.active = False
            self.make_avatar_speaks(self.goodbye_message)
            self.brain.clear_history()
        if self.active: 
            if self.sentence_chunking:
                for sentence, emotion in self.brain.generate_reply(_input):
                    print("Avatar : ", sentence)
                    #self.emotion_changer.change_emotion(emotion)
                    print("EMO: " + emotion)
                    #self.make_avatar_speaks(sentence)
                    self.audio_tasks_queue.put({'text': sentence, 'emotion': emotion})
                    #self.emotion_changer.change_emotion('neutral')
            else:
                full_answer = ""
                final_emotion = 'neutral'
                for sentence, emotion in self.brain.generate_reply(_input):
                    full_answer = full_answer + sentence + ' '
                    final_emotion = emotion
                self.audio_tasks_queue.put({'text': full_answer, 'emotion': final_emotion})

        if self.active == False and _input == self.activation_phrase:
            self.active = True
            self.make_avatar_speaks(self.hello_message)


    def run(self):
        self.asr.run(self._handle_asr_input)

        