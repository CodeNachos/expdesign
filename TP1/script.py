import os
import platform

import numpy as np
import sounddevice as sd

from time import sleep
from random import shuffle
from enum import Enum, unique
from scipy.io.wavfile import read
from scipy.io.wavfile import write
from matplotlib import pyplot as plt


# Paths to resources and output directories
RESSOURCES_PATH = "res"
PERIODIC_AUDIO_PATH = f"{RESSOURCES_PATH}/PeriodicAlong.wav"
APERIODIC_AUDIO_PATH = f"{RESSOURCES_PATH}/Aperiodic.wav"

OUTPUT_PATH = "output"
RECORDING_OUTPUT_PATH = f"{OUTPUT_PATH}/recordings"
PLOT_OUTPUT_PATH = f"{OUTPUT_PATH}/plots"

@unique
class Signal(Enum):
    """
    Enum class representing the type of signal: PERIODIC or APERIODIC.
    """
    PERIODIC = 1
    APERIODIC = 2

    def __str__(self) -> str:
        """
        Overrides the string representation of the Signal enum.
        Returns "Periodic" or "Aperiodic" based on the signal type.
        """
        match self:
            case self.PERIODIC:
                return "Periodic"
            case self.APERIODIC:
                return "Aperiodic"


def plot_signal(signal, sample_rate, duration: float = None, start: float = .0) -> None:
    """
    Plots the given signal with respect to the time.

    Parameters:
    - signal: The signal data to plot.
    - sample_rate: The sampling rate of the signal.
    - duration: Duration of the signal to plot (in seconds), None to plot the full signal.
    - start: The starting time in the signal (in seconds).
    """
    signal_duration = len(signal) / sample_rate

    # Validate start time
    if start < .0 or start >= signal_duration:
        start = .0
    
    # Validate and adjust duration
    if duration is None or duration > signal_duration or duration < .0:
        duration = signal_duration - start if start > .0 else signal_duration
    if start + duration > signal_duration:
        duration = signal_duration - start

    # Time axis
    t = np.arange(start * sample_rate, int((start + duration) * sample_rate))

    # Plot the signal
    _, axs = plt.subplots()
    axs.plot(t, signal[int(start * sample_rate):int(start + duration) * sample_rate])
    axs.set_title("Signal")
    axs.set_xlabel(f"Time (in samples of {sample_rate}Hz)")
    axs.set_ylabel("Amplitude")
    plt.show()


def plot_taps_with_beats(beats, taps) -> None:
    """
    Plots two signals (beats and taps) one under the other for comparison.

    Parameters:
    - beats: The beats signal.
    - taps: The taps signal.
    """
    samples = min(len(beats), len(taps))
    t = np.arange(0, samples)

    # Create subplots
    fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 12))
    fig.suptitle("The two signals")
    ax1.plot(t, beats[0:samples])
    ax2.plot(t, taps[0:samples])
    ax1.set_title("Beats")
    ax2.set_title("Taps")


def print_instructions() -> None:
    """
    Prints instructions for the user before the task begins.
    """
    print("\n------ INSTRUCTIONS -----\n" +
          "You will be presented with 2\n" +
          "consecutive tasks that follow\n" +
          "the same protocol.\n" +
          "Once each task starts, tap on\n" +
          "the microphone as soon as you\n" +
          "hear a beat for every beat.\n" +
          "------ ------------ -----\n")


def wait_input() -> None:
    """
    Waits for the user to press Enter to continue.
    """
    input("Press enter when ready to continue...")
    print("")


def clear_terminal():
    """
    Clears the terminal/console screen based on the operating system.
    Uses 'cls' for Windows and 'clear' for Linux/macOS.
    """
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def conduct_task(signal: Signal, subject_id: int = None, duration: float = None, 
                 countdown: int = 3, show_plot: bool = False) -> None:
    """
    Conducts the audio task, playing the audio and recording the user's taps.

    Parameters:
    - signal: The type of signal to play (PERIODIC or APERIODIC).
    - subject_id: Optional identifier for the subject.
    - duration: Duration of the task (in seconds). If None, uses the audio length.
    - countdown: Countdown before the task starts.
    - show_plot: Whether or not to display the plot of the signals after recording.
    """
    # Read the audio signal based on the signal type
    fs, audio_signal = read(PERIODIC_AUDIO_PATH if signal is Signal.PERIODIC 
                            else APERIODIC_AUDIO_PATH)

    # Ensure output directories exist
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    if not os.path.exists(RECORDING_OUTPUT_PATH):
        os.makedirs(RECORDING_OUTPUT_PATH)
    if not os.path.exists(PLOT_OUTPUT_PATH):
        os.makedirs(PLOT_OUTPUT_PATH)

    # Validate and adjust task duration
    audio_duration = len(audio_signal) / fs
    if ((not duration is None) and (duration > audio_duration)) or (duration is None):
        if not duration is None: 
            print("[WARNING]: specified task duration exceeds audio playback duration,"
                  "task duration will be set to playback duration.")
        duration = audio_duration

    # Start the countdown before the task starts
    if countdown < 0: countdown = 0
    countdown_timer = countdown
    while countdown_timer > 0:
        print(f"\rTask starts in {countdown_timer}...", end='', flush=True)
        countdown_timer -= 1
        sleep(1)
    print("\r------ Task running -----")

    # Play the audio and start recording
    print("Recording from microphone...")
    print("Tap whenever you hear a beat...")
    recorded_signal = sd.playrec(audio_signal[0:int(duration * fs)],
                                 samplerate=fs, channels=1, blocking=False)
    sleep(duration)
    print("Recording completed!")

    # Save the recording to a file
    subject = "" if subject_id is None else f"{subject_id}_"
    recording_filename = f"{RECORDING_OUTPUT_PATH}/{subject}{str(signal)}_task.wav"
    write(recording_filename, fs, recorded_signal)
    print(f"[LOG] Recording saved to {recording_filename}")

    # Plot and save the signals
    plot_taps_with_beats(audio_signal, recorded_signal)
    plt_filename = f"{PLOT_OUTPUT_PATH}/{subject}{str(signal)}_task.png"
    plt.savefig(plt_filename, dpi=300, bbox_inches='tight')
    print(f"[LOG] Signals plot saved to {plt_filename}")
    if show_plot: plt.show()

    print("\r----- Task completed ----")


def run_trial(start_signal: Signal = None, *args, **kwargs):
    """
    Runs the full trial, consisting of two tasks (PERIODIC and APERIODIC signals).
    
    Parameters:
    - start_signal: Optional starting signal type (PERIODIC or APERIODIC), default is random.
    - *args, **kwargs: Additional arguments to pass to conduct_task.
    """
    task_order = [s for s in Signal]
    shuffle(task_order)
    if not start_signal is None and task_order[0] != start_signal:
        task_order.reverse()
    
    clear_terminal()

    print_instructions()
    wait_input()

    # Conduct the first task
    conduct_task(task_order[0], *args, **kwargs)
    print("")

    print("Task 1 completed, one task left.")
    wait_input()

    # Conduct the second task
    conduct_task(task_order[1], *args, **kwargs)
    print("")

    print("All tasks completed, thanks for participating!")
    print("---")


if __name__ == "__main__":
    run_trial(duration=5)
