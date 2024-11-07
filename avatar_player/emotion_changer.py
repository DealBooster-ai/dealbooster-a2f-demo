from . omniverse_client.audio2face_rest_utils import set_emotion, get_emotion
import time
from threading import Thread, Lock
import numpy as np
from multiprocessing.dummy import Pool

class EmotionChanger:

    current_emotion = []
    target_emotion = []
    emotion_step = 0.2
    delta_time = 0.05

    EMOTIONS = {
        "neutral": [0,0,0,0,0,0,0,0,0,0],
        "amazement": [1,0,0,0,0,0,0,0,0,0],
        "anger": [0,1,0,0,0,0,0,0,0,0],
        "cheekness": [0,0,1,0,0,0,0,0,0,0],
        "disgust": [0,0,0,1,0,0,0,0,0,0],
        "fear": [0,0,0,0,1,0,0,0,0,0],
        "grief": [0,0,0,0,0,1,0,0,0,0],
        "joy": [0,0,0,0,0,0,1,0,0,0],
        "outofbreach": [0,0,0,0,0,0,0,1,0,0],
        "pain": [0,0,0,0,0,0,0,0,1,0],
        "sadness": [0,0,0,0,0,0,0,0,0,1]
    }

    def run_timer(self):
        def emotion_timer():
            while True:
                with self.lock:
                    current_emo = np.array(self.current_emotion)
                    target_emo = np.array(self.target_emotion)
                    if np.linalg.norm(current_emo - target_emo) < self.emotion_step:
                        self.current_emotion = self.target_emotion
                        current_emo = target_emo
                    if np.count_nonzero(current_emo - target_emo) != 0:
                        current_emo = current_emo + np.sign(target_emo - current_emo) * self.emotion_step
                        self.current_emotion = current_emo.tolist()
                        self.pool.apply_async(set_emotion, args=[self.a2f_url, self.a2f_instance, self.current_emotion])
                    
                    time.sleep(self.delta_time)
        
        t = Thread(target=emotion_timer)
        t.daemon = True
        t.start()
        

    def __init__(self, a2f_instance = '/World/audio2face/CoreFullface', a2f_host:str = 'localhost', a2f_api_port:int = 8011):
        self.a2f_url = f'http://{a2f_host}:{a2f_api_port}'
        self.a2f_instance = a2f_instance
        self.current_emotion = get_emotion(self.a2f_url, self.a2f_instance)
        self.target_emotion = self.current_emotion
        self.lock = Lock()
        self.pool = Pool(10)
        self.run_timer()

    def change_emotion(self, emotion_name, step=emotion_step):
        emo_vector = self.EMOTIONS['neutral']
        if emotion_name in self.EMOTIONS:
            emo_vector = self.EMOTIONS[emotion_name]
        with self.lock:
            self.target_emotion = emo_vector
        return