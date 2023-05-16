from pydub import AudioSegment
import glob
import os
from random import shuffle

NOISE_DIR = "C:/Users/nardi/website/kws/ia/data/noise/"
DATA_DIR = "C:/Users/nardi/website/kws/ia/data/keyword/"

def mix():
    noises = glob.glob(os.path.join(NOISE_DIR, "*.wav"))
    data = glob.glob(os.path.join(DATA_DIR, "*.wav"))
    shuffle(data)
    for i, noise in enumerate(noises):
        for j, audio in enumerate(data):
            sound1 = AudioSegment.from_file(audio)
            sound2 = AudioSegment.from_file(noise) - 7
            combined = sound1.overlay(sound2)
            combined.export(os.path.join(DATA_DIR, "{}_{}.wav".format(i, j)), format='wav')
