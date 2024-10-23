import os
import glob
import numpy as np
import pandas as pd

from io import TextIOWrapper
from praatio import textgrid
from scipy.io.wavfile import read
from scipy.signal import find_peaks
from matplotlib import pyplot as plt

SUBJECT_GROUPS = {"PWS": 1,
                  "PNS": 2}

CONDITIONS = {"Aperiodic"    : 1,
              "PeriodicAlong": 2}

DATAFILE_HEADER = "Subject\tGroup\tCondition\tFile\tTrain\tBeatNb\tBeatInstant\tTapInstant\n"

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


def open_datafile(fname:str, ovewrite:bool=True) -> TextIOWrapper :
    mode = 'w' if ovewrite else 'a'
    file_exists = os.path.exists(fname)
    f = open(fname, mode)
    if not file_exists or ovewrite:
        f.write(DATAFILE_HEADER)
    return f
    

def parse_filepath(fpath:str) -> tuple:
    parts = os.path.normpath(fpath).split(os.sep)[-3:]
    subject = int(parts[0][1:3])   # Assumes the first part starts with a character to skip
    group = parts[0][-3:]          # Assumes the last three characters denote the group
    condition = parts[1]           # Assumes the second part is the condition
    file = int(parts[2][4:8])      # Assumes the file part has a specific format
    return (subject, group, condition, file)

def get_textGrid_path(fpath_wav:str) -> str:
    base = os.path.splitext(fpath_wav)[0]
    return f"{base}.TextGrid"


def generate_datafile(dtfname:str="datafile.txt", data_dir:str="."):
    dtfile = open_datafile(dtfname, ovewrite=True)
    
    for file_path in glob.glob(data_dir + "/**/*.wav", recursive=True):  # process only .wav files
        fs, audio_signal = read(file_path)
        bips = audio_signal[:,0]
        taps = audio_signal[:,1]

        tg = textgrid.openTextgrid(get_textGrid_path(file_path), False)
        xmin,xmax,label = extractInfosFromTier(tg.getTier(tg.tierNames[0]))

        for t in range(len(label)):
            tpeaks_bips = find_peaks(bips[int(xmin[t]*fs):int(xmax[t]*fs)]/max(bips),
                                    height=0.05,
                                    distance=0.5*fs)[0]
            tpeaks_taps = find_peaks(taps[int(xmin[t]*fs):int(xmax[t]*fs)]/max(taps),
                                    height=0.05,
                                    distance=0.3*fs)[0]

            sbj, grp, cond, fl = parse_filepath(file_path)

            for k in range(0, min(len(tpeaks_bips), len(tpeaks_taps))):
                dtfile.write(f"{sbj}\t{SUBJECT_GROUPS[grp]}\t{CONDITIONS[cond]}\t{fl}\t{t+1}\t{k+1}\t{tpeaks_bips[k]/fs}\t{tpeaks_taps[k]/fs}\n")

    dtfile.close()

def get_datafile(dtfname:str):
    return pd.read_csv(dtfname, sep='\t')

if __name__ == "__main__":
    generate_datafile()
    