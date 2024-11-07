from avatar_player.player import AvatarPlayer
from avatar_player.emotion_changer import EmotionChanger
from avatar_player.avatar_brains.openai_brains import OpenAIBrains
from avatar_player.avatar_brains.dify_brains import DifyBrains
from avatar_player.tts.elevenlabs import ElevenLabs 
from avatar_player.emotion_changer import EmotionChanger
from avatar_player.asr.local_whisper import LocalWhisperASR

ACTIVE_AT_START = True
HELLO_MESSAGE = "Hello! My Name is Mary. How can I help yo today?"
CHARACTER_PROMPT = "You are a sales trainig avatar named Mary. A sales representative talk to you. \
                         You play as a customer. Make it tricky for the seales rep, reply with concerns, tricky questions, etc.\
                         Not more then one concern or question per reply. Reply concise and short as it is a fluent dialog. One-or two sentencies."

ACTIVATION_PHRASE = "hello Max"
DEACTIVATION_PHRASE = "goodbye Max"

'''avatar_player = AvatarPlayer(
    brain=OpenAIBrains(CHARACTER_PROMPT),
    tts_engine=PYTTSx4(voice_index=0),
    asr=LocalWhisperASR(model='base'),
    a2f_host='localhost',
    a2f_player_instance='/World/audio2face/PlayerStreaming',
    a2f_sample_rate=22050,
    activation_phrase=ACTIVATION_PHRASE,
    deactivation_phrase=DEACTIVATION_PHRASE,
    hello_message=HELLO_MESSAGE,
    goodbye_message="Thank you for visiting, goodbye!"
)'''
avatar_player = AvatarPlayer(
    brain=DifyBrains(api_key='app-R4OXYgWa6szBBXRdpCiBcWAq', endpoint='https://api.dify.ai/v1'),
    tts_engine=ElevenLabs("EXAVITQu4vr4xnSDxMaL"),
    asr=LocalWhisperASR(model='base'),
    a2f_host='localhost',
    a2f_player_instance='/World/audio2face/PlayerStreaming',
    a2f_sample_rate=22050,
    activation_phrase=ACTIVATION_PHRASE,
    deactivation_phrase=DEACTIVATION_PHRASE,
    hello_message=HELLO_MESSAGE,
    goodbye_message="Thank you for visiting, goodbye!"
)

avatar_player.active = ACTIVE_AT_START

avatar_player.run()