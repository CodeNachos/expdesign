import numpy as np
from scipy.io.wavfile import read
import sounddevice as sd
from time import sleep
from scipy.io.wavfile import write
from matplotlib import pyplot as plt

from enum import Enum, unique
import os

RESSOURCES_PATH = "res"
PERIODIC_AUDIO_PATH = f"{RESSOURCES_PATH}/PeriodicAlong.wav"
APERIODIC_AUDIO_PATH = f"{RESSOURCES_PATH}/Aperiodic.wav"

OUTPUT_PATH = "output"
RECORDING_OUTPUT_PATH = f"{OUTPUT_PATH}/recordings"
PLOT_OUTPUT_PATH = f"{OUTPUT_PATH}/plots"

@unique
class Signal(Enum):
    PERIODIC = 1
    APERIODIC = 2

    def __str__(self):
        match self:
            case self.PERIODIC:
                return "Periodic"
            case self.APERIODIC:
                return "Aperiodic"


def conduct_task(signal:Signal, subject_id:int=None, duration:float=None, 
                 countdown:int=3, show_plot:bool=False):
    fs, audio_signal = read(PERIODIC_AUDIO_PATH if signal is Signal.PERIODIC 
                            else APERIODIC_AUDIO_PATH)
    
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    if not os.path.exists(RECORDING_OUTPUT_PATH):
        os.makedirs(RECORDING_OUTPUT_PATH)
    if not os.path.exists(PLOT_OUTPUT_PATH):
        os.makedirs(PLOT_OUTPUT_PATH)

    audio_duration = len(audio_signal)/fs
    if ((not duration is None) and (duration > audio_duration)) or (duration is None):
        if not duration is None: 
            print("[WARNING]: specified task duration exceeds audio playback duration,"
                "task duration will be set to playback duration.")
        duration = audio_duration 
    

    if countdown < 0: countdown = 0
    countdown_timer = countdown
    while countdown_timer > 0:
        print(f"\rTask starts in {countdown_timer}...", end='', flush=True)
        countdown_timer -= 1
        sleep(1)
    print("\r------ Task running -----")

    print("Recording from microphone...")
    recorded_signal = sd.playrec(audio_signal[0:int(duration*fs)],
                                 samplerate=fs, channels=1, blocking=False)
    sleep(duration)
    print("Recording completed!")


    subject = "" if subject_id is None else f"{subject_id}_"
    recording_filename = f"{RECORDING_OUTPUT_PATH}/{subject}{str(signal)}_task.wav"
    write(recording_filename, fs, recorded_signal)
    print(f"Recording saved to {recording_filename}")

    plot_taps_with_beats(audio_signal, recorded_signal)
    plt_filename = f"{PLOT_OUTPUT_PATH}/{subject}{str(signal)}_task.png"
    plt.savefig(plt_filename,dpi=300, bbox_inches='tight')
    print(f"Signals plot saved to {plt_filename}")
    if show_plot: plt.show()

    print("\r----- Task completed ----")


def plot_taps_with_beats(beats, taps):
    samples = min(len(beats), len(taps))
    t = np.arange(0, samples)
    fig,(ax1,ax2) = plt.subplots(2,figsize=(10,12)) 
    fig.suptitle("The two signals")
    ax1.plot(t,beats[0:samples])
    ax2.plot(t,taps[0:samples])  
    ax1.set_title("Beats") 
    ax2.set_title("Taps")


def plot_signal(signal, sample_rate, duration:float=None, start:float=.0):
    signal_duration = len(signal)/sample_rate
    
    if start < .0 or start >= signal_duration:
        start = .0
    
    if duration is None or duration > signal_duration or duration < .0:
        duration = signal_duration - start if start > .0 else signal_duration

    if start + duration > signal_duration:
        duration = signal_duration - start

    t = np.arange(start*sample_rate, int((start+duration)*sample_rate))
    _, axs = plt.subplots() 
    axs.plot(t, signal[int(start*sample_rate):int(start+duration)*sample_rate]) 
    axs.set_title("Signal") 
    axs.set_xlabel(f"Time (in samples of {sample_rate}Hz)")
    axs.set_ylabel("Amplitude") 
    plt.show() 


if __name__ == "__main__":
    conduct_task(Signal.PERIODIC, duration=5, countdown=0)