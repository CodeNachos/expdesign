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

#print("'Sujet\tGroupe\tCondition\tFile\tTrain\tBeatNb\tBeatInstant\tTapInstant\n'")
#print(f"")



def detect_fast_increases(signal, threshold_increase=0.5, threshold_decrease=-0.5):
    """
    Detect regions in the signal where there is a fast increase or decrease.
    Parameters:
    - signal: The input signal (1D numpy array).
    - threshold_increase: Threshold for detecting rapid increases in the signal.
    - threshold_decrease: Threshold for detecting rapid decreases in the signal.
    """
    # Compute the first derivative (rate of change) of the signal
    derivative = np.diff(signal)

    # Detect regions of rapid increase (when the derivative exceeds the increase threshold)
    start_indices = np.where(derivative > threshold_increase)[0]
    # Detect regions of rapid decrease (when the derivative goes below the decrease threshold)
    end_indices = np.where(derivative < threshold_decrease)[0]
    print(len(start_indices))
    
    # Filter start and end indices to match (end should be after the start)
    patterns = []
    for start in start_indices:
        # Find the first end index that comes after the start index
        possible_ends = end_indices[end_indices > start]
        if len(possible_ends) > 0:
            end = possible_ends[0]
            patterns.append((start, start))
    print(f"found {len(patterns)} patterns")
    return patterns, derivative

def plot_detected_patterns(signal, patterns, derivative=None):
    """
    Plot the original signal and highlight the detected rapid increase/decrease regions.
    Optionally also plot the derivative of the signal.
    """
    plt.figure(figsize=(10, 5))
    
    # Plot the original signal
    plt.plot(signal, label='Signal')
    
    # Highlight the regions where fast increase/decrease were detected
    for (start, end) in patterns:
        plt.axvspan(start, end, color='red', alpha=0.3, label='Detected Pattern')
    
    # Optionally plot the derivative if provided
    if derivative is not None:
        plt.plot(derivative, label='Derivative', linestyle='--')
    
    plt.legend()
    plt.show()

# Example signal (replace with your actual signal)
signal =taps[int(xmin[0]*fs):int(xmax[0]*fs)]/max(taps)

# Detect patterns based on rapid increases and decreases in the signal
patterns, derivative = detect_fast_increases(signal, threshold_increase=0.2, threshold_decrease=-0.5)

# Plot the detected patterns
plot_detected_patterns(signal, patterns, derivative=derivative/max(derivative))

#import glob
#root_dir = "."
#for file_path in glob.glob(root_dir + "/**/*.wav", recursive=True):  # Process only .txt files
#    print(file_path)
#    print(file_path.split('\\')[-3:])