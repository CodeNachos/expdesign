from scipy.io.wavfile import read
import sounddevice as sd
from time import sleep
from scipy.io.wavfile import write

fs, audio_signal = read('PeriodicAlong.wav')
print("recording...",end="", flush=True)
#sd.play(audio_signal, fs)
recorded_signal = sd.rec(int(10 * fs), samplerate=fs, channels=1)
sd.wait()

print("end")
write("output.wav", fs, recorded_signal)