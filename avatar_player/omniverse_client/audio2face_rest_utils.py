import requests
import json

def set_emotion(host, a2f_instane, emotion_vector):
    url = f'{host}/A2F/A2E/SetEmotion'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {
        "a2f_instance": a2f_instane,
        "emotion": emotion_vector
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response


def get_emotion(host, a2f_instane):
    url = f'{host}/A2F/A2E/GetEmotion'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    payload = {
        "a2f_instance": a2f_instane,
        "as_vector": True
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()['result']