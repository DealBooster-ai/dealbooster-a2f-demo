from . import IAvatarBrians, Utterance, Phrase, EnhancedJSONEncoder
from openai import OpenAI
import json
import os

class OpenAIBrains(IAvatarBrians):

    system_prompt = ""

    EMOTIONAL_ADDITION = "Give concise replies. Don't use special formatting, links, or numbered lists. \
        Provide your answer in valid JSON format only with 2 fields: text and emotion. No additional formatting needed. The emotional reaction is very important, \
        don't restrict yourself to a business-type emotional reaction. \
        Emotion of your response may be one of the above: neutral, amazement, anger, cheekness, disgust, fear, grief, joy, outofbreach, pain, sadness. \
        your entire response/output is going to consist of a single JSON object \{\}, and you will NOT wrap it within JSON md markers"

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt + self.EMOTIONAL_ADDITION
        return super().__init__()

    def convert_history(self):
        open_ai_history = []
        for history_item in self.message_history:
            if history_item.role == "assistant":
                open_ai_history.append(
                    {"role":history_item.role, "content": json.dumps(history_item.phrases[0], cls=EnhancedJSONEncoder)}
                )
            else:
                open_ai_history.append(
                    {"role":history_item.role, "content": history_item.text()}
                )
        return open_ai_history

    def generate_reply(self, user_utterance):
        x = Utterance("user", "", [Phrase(user_utterance, "")])
        self.message_history.append(x)
        open_ai_history = self.convert_history()
        openai = OpenAI(
            api_key=os.environ.get('OPEN_AI_KEY')
        )
        messages_history = [{"role": "system", "content": self.system_prompt}]
        messages_history = messages_history + open_ai_history
        completion = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages_history
        )
        openai_response = completion.choices[0].message.content
        assistan_utterace = Utterance("assistant", "", [])
        try:
            openai_response = json.loads(openai_response) 
            response_text = openai_response["text"]
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
                yield sentence, openai_response["emotion"]
            assistan_utterace.phrases.append(Phrase(openai_response["text"], openai_response["emotion"]))
        except:
            yield openai_response, "neutral"
            assistan_utterace.phrases.append(Phrase(openai_response, "neutral"))
        self.message_history.append(assistan_utterace)
        