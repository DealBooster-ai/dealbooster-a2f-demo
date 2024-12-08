from . import IAvatarBrians, Utterance, Phrase, EnhancedJSONEncoder
import requests
import uuid

class DifyBrains(IAvatarBrians):

    completion_client = None

    conversation_id = ""
   
    def __init__(self, api_key, endpoint = "http://localhost/v1"):
        self.api_key = api_key
        self.endpoint = endpoint
        return super().__init__()

 
    def generate_reply(self, user_utterance):
        payload = {
            "inputs": {},
            "query": user_utterance,
            "response_mode": "blocking",
            "conversation_id": self.conversation_id,
            "user": "abc-123",
        }
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        response = requests.post(url=f'{self.endpoint}/chat-messages', headers=headers, json=payload)

        response_text = response.json().get('answer')
        self.conversation_id = response.json().get("conversation_id")
        response_array = response_text.split()
        output_array = []
        s = ''
        for word in response_array:
            if word.endswith(('.', '?', '!')):
                s = s + ' ' + word
                output_array.append(s)
                s = ''
            else:
                s = s + ' ' + word                
        for sentence in output_array:       
            yield sentence, "neutral"