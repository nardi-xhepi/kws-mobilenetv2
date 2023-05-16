from pydub import AudioSegment
from pydub.silence import split_on_silence
import os

PATH_TO_AUDIO = "C:/Users/nardi/website/kws/ia/user_data/audio.wav"
DATA_DIR = "C:/Users/nardi/website/kws/ia/data/keyword/"

def split():
    sound_file = AudioSegment.from_file(PATH_TO_AUDIO)

    audio_chunks = split_on_silence(sound_file,
                                    min_silence_len=500,
                                    silence_thresh=-45)

    for i, chunk in enumerate(audio_chunks):
        file = os.path.join(DATA_DIR, "chunk{}.wav".format(i))
        chunk.export(file, format="wav")