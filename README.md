# DealBooster Avatar Demo
## Project Description
A demo version of the avatar.
This project shopuld be runned on RTX-based GPU powered computer.
As a backentd it utilizes the server-side LLM-based bot.
Source code of this bot could be found in the [dealbooster-ll-bot repo](https://github.com/DealBooster-ai/dealbooster-llm-bot).

## System Requirements
|  Element   | Minimum Specifications |
|  ----  | ----  |
| OS Supported	  | 	Windows 10 64-bit (Version 1909 and above) |
| CPU  | 	Intel I7, AMD Ryzen 2.5GHz or greater |
| CPU Cores  | 	4 or higher |
| RAM  | 	16 GB or higher |
| Storage  | 	500 Gb SSD or higher |
| GPU  | 	Any RTX GPU |
| VRAM  | 	6 GB or higher |
| Min. Video Driver Version  | 	See latest drivers [here](https://developer.nvidia.com/omniverse/driver) |

# Prepare and run

## Pulling the project
To pull the project you'll need Git LFS, as there are huge 3D assets.
Follow [Installing Git LFS Guide](https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage).

Then you can pull the project
```(bash)
git clone git@github.com:DealBooster-ai/dealbooster-a2f-demo.git
```
Or just [download](https://github.com/DealBooster-ai/dealbooster-a2f-demo/archive/refs/heads/main.zip) it as archive from github.

## NVIDIA Audio2Face installation
### Download and Install Omniverse Launcher
[NVIDIA Omniverse](https://docs.omniverse.nvidia.com/prod_install-guide/prod_install-guide.html) is a development platform for 3D simulation and design collaboration, it is free for individual, you can download Omniverse Launcher [here](https://www.nvidia.com/en-us/omniverse/download/).

I also recommend you to watch this [video tutorial](https://www.youtube.com/watch?v=Ol-bCNBgyFw), which guides you through the installation process. 

| ![](https://i.imgur.com/4imNFt1.jpg) | 
|:--:| 
| *Omniverse Launcher* |

### Install Omniverse Audio2Face
| ![](https://i.imgur.com/6kbTCRW.jpg) | 
|:--:| 
| *Omniverse apps* |

Once you got Omniverse Launcher installed, you can immediate access to all the apps, including [Omniverse Audio2Face](https://www.nvidia.com/en-us/omniverse/apps/audio2face/). Next, simply install Omniverse Audio2Face version **2023.2.0** and you're good to go.

| ![](https://i.imgur.com/N94KDTc.png) | 
|:--:| 
| *Omniverse Audio2Face* |


## Python instllation and setup

### Install Python 3.8
Download for windows.
Install and reboot the system.
Test it by runnig this commain in PowerShell:
```(bash)
python -V
```

### Create and activate virtual environment
Run PowerShell and navigate to this folder.

Create and activate the environment, install dependencies for python
```(bash)
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If you got an error while activating environment, run before it
```(bash)
Set-ExecutionPolicy Unrestricted -Scope Process
```

## Run the avatar
### Open Audio2Face scene
1. Open Omniverse Launcher
2. Run Audio2Face application
3. In the content section, navigate to ./3DScene folder and open AvatarStreaming.usd
4. Once the scene is loaded, press play button to run the animation

### Launch the python app
1. Open PowerShell
2. Navigate to this folder
3. Activate the environment
```(bash)
.venv\Scripts\activate
```
If you got an error while activating environment, run before it
```(bash)
Set-ExecutionPolicy Unrestricted -Scope Process
```
4. Run the app
```(bash)
python .\avatar.py
```

### Make it nice
If you have 2 displays, you may see speech output inthe power shell window on one of them and the 3D scen on the other.

To have a full-screen 3D avatr, press F11.

You can use [OBS Studio](https://obsproject.com/) to make [Virtual Camera that shows the avatar in Zoom](https://www.youtube.com/watch?v=Ki9E8mxsXRI&t=2s) or Google Meet.

With [VB-Cable A+B](https://shop.vb-audio.com/en/win-apps/12-vb-cable-ab.html?SubmitCurrency=1&id_currency=1) you can connect you computer's audio input and output to Zoom or Google Meet.

As follows:

* Zoom Microphone Device: CABLE-A Output
* Zoom Speaker Device: CABLE-B Input
* System Input Sound Device: CABLE-B Output
* System Output Sound Device: CABLE-A Input

**System Sound Setup:**

![System Sound Setup](https://github.com/DealBooster-ai/dealbooster-a2f-demo/blob/main/imgs/system-sound-setup.png?raw=true)

**Zoom Setup:**

![Zoom Setup](https://github.com/DealBooster-ai/dealbooster-a2f-demo/blob/main/imgs/zoom-sound-setup.png?raw=true)

**Google Meet Setup:**

![Meet Setup](https://github.com/DealBooster-ai/dealbooster-a2f-demo/blob/main/imgs/meet-sound-setup.png?raw=true)

As result your avatra will act as a real agent. You just need to join a call for it.

**That's it! Good luck!**
#
#
#
#
#
#

## How It Works
![](https://i.imgur.com/BZIBUAt.png)
#### ***Automatic Speech Recognition, ASR***
Upon receiving user's request, the [SpeechRecognition API](https://pypi.org/project/SpeechRecognition/) records the frequencies and sound waves from user's voice and translates them into text. 
#### ***Language Understanding***
[Sentence-Transformer](https://www.sbert.net/) is for state-of-the-art sentence, text and image embeddings that can encode input questions into feature vectors. The feature vectors represent entire sentences and their semantic information, this helps the machine in understanding the context, intention, and other nuances in the entire text.

We’ll conduct a similarity search, comparing a user input question to a list of FAQs and return the most likely answers by [Facebook’s Similarity Search API](https://ai.facebook.com/tools/faiss/).
#### ***Text To Speech***
The avatar's voice is fully synthesized by the [Gtts API](https://pypi.org/project/gTTS/), which turns text into natural-sounding speech. The synthesized voice is also used to drive the avatar's facial animation.
#### ***Omniverse Audio2Face***
![](https://i.imgur.com/7ioYQHj.png)

Omniverse Audio2Face is an application brings our avatars to life. With [Omniverse Audio2Face](https://www.nvidia.com/en-us/omniverse/apps/audio2face/), anyone can now create realistic facial expressions and emotions to match any voice-over track. The technology feeds the audio input into a pre-trained Deep Neural Network, based on NVIDIA and the output of the network drives the facial animation of 3D characters in real-time.

## How to Install and Run the Project
Before you begin, you'll need to clone the repository with the template code used in this repo. Open your Terminal app and find a directory where you'd like to store the code. Run this command to clone the GitHub App template repository:

```
$ git clone https://github.com/metaiintw/build-an-avatar-with-ASR-TTS-Transformer-Omniverse-Audio2Face.git
```
#### Creating an environment from an environment. yml file
Make sure Anaconda is installed on your local machine. Use the following command to install packages included in requirements.yml:
```
$ conda env create -f /path/to/requirements.yml
```
#### Omniverse Audio2Face setup
To get our Python program interacts with Omniverse Audio2Face, you should use streaming audio player that allows developers to stream audio data from an external source or applications via the gRPC protocol. 

| ![](https://i.imgur.com/qZUQVS0.png) | 
|:--:| 
| *streaming audio player allows developers to stream audio data from an external source* |

This [tutorial](https://www.youtube.com/watch?v=qKhPwdcOG_w&t=17s) showcases how to create an audio player and connect it to the audio2face instance using the omnigraph editor.