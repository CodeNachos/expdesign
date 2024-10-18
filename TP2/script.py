from matplotlib import pyplot as plt
import numpy as np
from scipy.io.wavfile import read
from praatio import textgrid
from scipy.signal import find_peaks

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

filename = "Grp5/S13-PWS/PeriodicAlong/S13_0009-BaT.wav"

fs, audio_signal = read(filename)
bips = audio_signal[:,0]
taps = audio_signal[:,1]

tg = textgrid.openTextgrid("Grp5/S13-PWS/PeriodicAlong/S13_0009-BaT.TextGrid", False)
xmin,xmax,label = extractInfosFromTier(tg.getTier(tg.tierNames[0]))

tpeaks_bips = find_peaks(bips[int(xmin[0]*fs):int(xmax[0]*fs)]/max(bips),
                         height=0.05,
                         distance=0.5*fs)[0]
tpeaks_taps = find_peaks(taps[int(xmin[0]*fs):int(xmax[0]*fs)]/max(taps),
                         height=0.02,
                         distance=0.3*fs)[0]

print("'Sujet\tGroupe\tCondition\tFile\tTrain\tBeatNb\tBeatInstant\tTapInstant\n'")
print(f"")

import glob
root_dir = "."
for file_path in glob.glob(root_dir + "/**/*.wav", recursive=True):  # Process only .txt files
    print(file_path.split('\\')[-3:])