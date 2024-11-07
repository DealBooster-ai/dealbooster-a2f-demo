# Local deployment of whisper ASR service
To use `avatar_player.asr.local_whisper.LocalWhisperASR`class for avatr's ASR you need to follow some additional steps.


1. [Download](https://developer.nvidia.com/cuda-downloads?target_os=Windows) and install NVIDIA CUDA Toolkit.

2. Reboot

3. INstall dependencies
```
pip install -r .\avatar_player\asr\local_whisper\requirements.txt
```

If something goes wrong or whisper run on CPU, change pytorch version in the requirements txt to be compatible with your version of driver/cuda.