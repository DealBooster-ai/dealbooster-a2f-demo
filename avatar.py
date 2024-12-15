from avatar_player.player import AvatarPlayer
from avatar_player.avatar_brains.dify_brains import DifyBrains
from avatar_player.tts.elevenlabs_multi import ElevenLabsMultilingual
from avatar_player.tts.elevenlabs import ElevenLabs
from avatar_player.asr.local_whisper.whisper_hf import WhisperHF
import argparse

parser = argparse.ArgumentParser(description='Avatar Player')

parser.add_argument('-d', '--dify', default='app-R4OXYgWa6szBBXRdpCiBcWAq')
parser.add_argument('-a', '--asr-model', default='openai/whisper-base')
parser.add_argument('-v', '--voice', default='21m00Tcm4TlvDq8ikWAM')
parser.add_argument('-m', '--mic', default=None, type=int)

args = parser.parse_args()

print(args)

ACTIVE_AT_START = True

avatar_player = AvatarPlayer(
    brain=DifyBrains(api_key=args.dify, endpoint='https://api.dify.ai/v1'),
    tts_engine=ElevenLabsMultilingual(voice_id=args.voice),
    asr=WhisperHF(model=args.asr_model, device_id=args.mic)
)

avatar_player.active = ACTIVE_AT_START

avatar_player.run()