import os

import numpy as np

from io import TextIOWrapper
from praatio import textgrid
from scipy.io.wavfile import read
from scipy.signal import find_peaks
from matplotlib import pyplot as plt

SUBJECT_GROUPS = {"PWS": 1,
                  "PNS": 2}

CONDITIONS = {"Aperiodic"    : 1,
              "PeriodicAlong": 2}

DATAFILE_HEADER = "Sujet\tGroupe\tCondition\tFile\tTrain\tBeatNb\tBeatInstant\tTapInstant\n"

def plot_taps_with_beats(beats, taps, sample_rate, duration: float = None, start: float = .0) -> None:
    beats_duration = len(beats) / sample_rate

    # Validate start time
    if start < .0 or start >= beats_duration:
        start = .0
    
    # Validate and adjust duration
    if duration is None or duration > beats_duration or duration < .0:
        duration = beats_duration - start if start > .0 else beats_duration
    if start + duration > beats_duration:
        duration = beats_duration - start

    # Time axis
    t = np.arange(start * sample_rate, int((start + duration) * sample_rate))
    
    # Plot the signal
    _, axs = plt.subplots()
    axs.plot(t, beats[int(start * sample_rate):int((start + duration) * sample_rate)], label='Beats')
    axs.plot(t, taps[int(start * sample_rate):int((start + duration) * sample_rate)], label='Taps')
    axs.set_title("Signal")
    axs.set_xlabel(f"Time (in samples of {sample_rate}Hz)")
    axs.set_ylabel("Amplitude")
    plt.legend()
    plt.show()


def extractInfosFromTier(Tier):
    xmi = []
    xma = []
    lab = []

    for start, end, label in Tier.entries:
        xmi.append(start)
        xma.append(end)
        lab.append(label)
    return xmi, xma, lab


def open_datafile(fname:str, ovewrite:bool=False) -> TextIOWrapper :
    try:
        file_exists = os.path.file_exists(fname)
        f = open(fname, 'a')
        if not file_exists:
            f.write(DATAFILE_HEADER)
        return f
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    



if __name__ == "__main__":
    dtfname = "output.txt"
    dtfile = open_datafile(dtfname)
    dtfile.close()