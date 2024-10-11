from scipy.io.wavfile import read
import sounddevice as sd
from time import sleep
from scipy.io.wavfile import write

fs, audio_signal = read('PeriodicAlong.wav')
print("recording...",end="", flush=True)
recorded_signal = sd.playrec(audio_signal,channels=1,samplerate=fs, blocksize=1024, latency="high") 
sleep(10)
print("end")
sd.stop()
write("output.wav", fs, recorded_signal)