import os
import glob
import numpy as np
import pandas as pd

from io import TextIOWrapper
from praatio import textgrid
from scipy.io.wavfile import read
from scipy.signal import find_peaks
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors

# Dictionary mapping subject groups to integer values
SUBJECT_GROUPS = {"PWS": 1,   # PWS: People who stutter
                  "PNS": 2}   # PNS: People who do not stutter

# Dictionary mapping conditions to integer values
CONDITIONS = {"Aperiodic"    : 1,  # Condition: Aperiodic
              "PeriodicAlong": 2}  # Condition: Periodic Along

# Header for the output data file
DATAFILE_HEADER = "Subject\tGroup\tCondition\tFile\tTrain\tBeatNb\tBeatInstant\tTapInstant\n"


def plot_taps_with_beats(beats, taps, sample_rate, start: float = .0, 
                         duration: float = None, xsamples:bool=False) -> None:
    """
    Plots both beats and taps with respect to the time.

    Parameters:
    - beats: The beats signal array.
    - taps: The taps signal array.
    - start: The starting time in the signal (in seconds).
    - duration: Duration of the signal to plot (in seconds), None to plot the full signal.
    - xsamples: If true the signals is ploted as a function of sample number rather than time
    """
    
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
    if xsamples:
        t = np.arange(start * sample_rate, int((start + duration) * sample_rate))
    else:
        t = np.arange(start, start + duration, 1/sample_rate)
    
    # Plot the signal
    _, axs = plt.subplots()
    axs.plot(t, beats[int(start * sample_rate):int((start + duration) * sample_rate)], label="Beats")
    axs.plot(t, taps[int(start * sample_rate):int((start + duration) * sample_rate)], label="Taps")
    axs.set_title("Signal")
    if xsamples:
        axs.set_xlabel(f"Time (in samples of {sample_rate}Hz)")
    else:
        axs.set_xlabel(f"Time (s)")
    axs.set_ylabel("Amplitude")
    plt.legend()
    plt.show()


def extractInfosFromTier(Tier):
    """
    Extracts the start times, end times, and labels from a given Tier.
    
    Args:
        Tier (textgrid.TextGridTier): A tier object from which to extract information.
        
    Returns:
        tuple: Three lists containing start times (xmi), end times (xma), and labels (lab) respectively.
    """
    xmi = []  # List of start times
    xma = []  # List of end times
    lab = []  # List of labels

    # Iterate through the entries in the Tier (start, end, label)
    for start, end, label in Tier.entries:
        xmi.append(start)
        xma.append(end)
        lab.append(label)
    return xmi, xma, lab


def open_datafile(fname: str, overwrite: bool = True) -> TextIOWrapper:
    """
    Opens or creates a data file for writing, optionally appending data if it already exists.
    
    Args:
        fname (str): The name of the file to open.
        overwrite (bool): If True, overwrites the existing file; otherwise, appends to the file.
        
    Returns:
        TextIOWrapper: A file object for writing.
    """
    mode = 'w' if overwrite else 'a'  # Open in write ('w') or append ('a') mode
    file_exists = os.path.exists(fname)
    f = open(fname, mode)

    # If file doesn't exist or we are overwriting, write the header
    if not file_exists or overwrite:
        f.write(DATAFILE_HEADER)

    return f


def parse_filepath(fpath: str) -> tuple:
    """
    Extracts subject, group, condition, and file number from a given file path.
    
    Args:
        fpath (str): The file path to parse.
        
    Returns:
        tuple: A tuple containing subject (int), group (str), condition (str), and file number (int).
    """
    parts = os.path.normpath(fpath).split(os.sep)[-3:]  # Get the last three parts of the path
    subject = int(parts[0][1:3])   # Assumes first part starts with a character followed by subject number
    group = parts[0][-3:]          # Assumes last three characters of the first part represent the group
    condition = parts[1]           # Assumes second part of the path is the condition
    file = int(parts[2][4:8])      # Assumes the file part has a specific format with a 4-digit number
    return (subject, group, condition, file)


def get_textGrid_path(fpath_wav: str) -> str:
    """
    Generates the path to the corresponding TextGrid file for a given .wav file.
    
    Args:
        fpath_wav (str): The file path of the .wav file.
        
    Returns:
        str: The file path of the corresponding TextGrid file.
    """
    base = os.path.splitext(fpath_wav)[0]  # Remove the .wav extension from the file
    return f"{base}.TextGrid"              # Return the path with .TextGrid extension


def process_data(dtfname: str = "datafile.txt", data_dir: str = "."):
    """
    Processes all .wav files in a directory, extracts beat and tap data, and writes results to a data file.
    
    Args:
        dtfname (str): Name of the output data file.
        data_dir (str): Directory containing the .wav files to process.
    """
    # Open or create the output data file
    dtfile = open_datafile(dtfname, overwrite=True)
    
    # Process all .wav files in the specified directory recursively
    for file_path in glob.glob(data_dir + "/**/*.wav", recursive=True):
        print(file_path)
        # Load the audio signal
        fs, audio_signal = read(file_path)
        bips = audio_signal[:,0]  # First channel for beats
        taps = audio_signal[:,1]  # Second channel for taps
        #bips = np.where(bips < 0, 0, bips)
        #taps = np.where(taps < 0, 0, taps)
        #bips = bips/ max(bips)
        #taps = taps/ max(taps)
        #bips = np.diff(bips)
        #taps = np.diff(taps)

        # Open the corresponding TextGrid file
        tg = textgrid.openTextgrid(get_textGrid_path(file_path), False)
        
        # Extract information from the tiers in the TextGrid
        xmin, xmax, label = extractInfosFromTier(tg.getTier(tg.tierNames[0]))  # Main tier
        bips_tier = tg.getTier(tg.tierNames[1])  # Bips tier
        taps_tier = tg.getTier(tg.tierNames[2])  # Taps tier
        
        # Loop through each label (trial) in the tier
        for t in range(len(label)):
            
            # Find peaks for bips and taps between xmin and xmax
            tpeaks_bips = find_peaks(bips[int(xmin[t]*fs):int(xmax[t]*fs)] / max(bips),
                                     height=0.1,
                                     distance=0.3 * fs)[0] + int(xmin[t]*fs)
            tpeaks_taps = find_peaks(taps[int(xmin[t]*fs):int(xmax[t]*fs)] / max(taps),
                                     height=0.05,
                                     distance=0.1 * fs,
                                     prominence=0.1)[0] + int(xmin[t]*fs)
            #plot_taps_with_beats(bips[int(xmin[t]*fs):int(xmax[t]*fs)] / max(bips), taps[int(xmin[t]*fs):int(xmax[t]*fs)] / max(taps), fs, xsamples=False)
            # Parse information from the file path
            sbj, grp, cond, fl = parse_filepath(file_path)
            # Write peaks data to the data file
            couples = get_couples(tpeaks_bips, tpeaks_taps,cond)
        
            for n,tap in couples.items():
                dtfile.write(f"{sbj}\t{SUBJECT_GROUPS[grp]}\t{CONDITIONS[cond]}\t{fl}\t{t + 1}\t{n + 1}\t{tpeaks_bips[n] / fs}\t{tap/ fs}\n")
            

#           for k in range(0, min(len(tpeaks_bips), len(tpeaks_taps))):
#               dtfile.write(f"{sbj}\t{SUBJECT_GROUPS[grp]}\t{CONDITIONS[cond]}\t{fl}\t{t+1}\t{k+1}\t{tpeaks_bips[k]/fs}\t{tpeaks_taps[k]/fs}\n")

            # Update TextGrid tiers with new peaks
            for k in range(len(tpeaks_bips)):
                bips_tier.insertEntry((tpeaks_bips[k] / fs, ""), collisionMode='replace', collisionReportingMode='silence')
            for k in range(len(tpeaks_taps)):
                taps_tier.insertEntry((tpeaks_taps[k] / fs, ""), collisionMode='replace', collisionReportingMode='silence')
            
        # Save the updated TextGrid file
        tg.save(get_textGrid_path(file_path), format="long_textgrid", includeBlankSpaces=True)
        
    # Close the data file
    dtfile.close()



def get_datafile_as_dataframe(dtfname: str):
    """
    Reads the output data file into a pandas DataFrame.
    
    Args:
        dtfname (str): Name of the data file to read.
        
    Returns:
        pd.DataFrame: A DataFrame containing the data from the file.
    """
    return pd.read_csv(dtfname, sep='\t')


def get_couples(b, t, cond):
    couples = {}
    bips = b.copy().tolist()
    taps = t.copy().tolist()
    last_bip = 0
    if cond==1:
        for n,bip in enumerate(bips):
            next_bip = bips[n+1] if n<len(bips)-1 else None
            ignored = []
            for tap in taps:
                if tap in ignored or tap > next_bip-((next_bip-bip)*25/100):#certainly an ignored bip
                    break
                elif next_bip is None and bip <= tap:
                    couples.update({n:tap})
                    ignored.append(tap)
                elif bip <= tap < next_bip:
                    couples.update({n:tap})
                    ignored.append(tap)
                else:
                    continue
    else :
        between_taps = []
        for n,bip in enumerate(bips):
            next_bip = bips[n+1] if n<len(bips)-1 else None
            for tap in taps:
                if next_bip is not None and tap > next_bip-((next_bip-bip)*25/100):#certainly an ignored bip
                    break
                elif next_bip is None:
                    between_taps.append(tap)
                elif last_bip <= tap < next_bip:
                    between_taps.append(tap)
                else:
                    continue

            if len(between_taps) > 2:#check for too much taps, remove all bcs we can't choose one to couple
                couples.update({n: tap})
            elif len(between_taps) == 2 or len(between_taps) == 1:
                # the first go with the bip, the second (if present) will be compute next loop
                couples.update({n: between_taps[0]})
                taps.remove(between_taps[0])
            #case len(between_taps) == 0 there is no taps for this bip
            between_taps = []
            last_bip = bip
    return couples


if __name__ == "__main__":
    process_data()
    