from scipy.io.wavfile import read
from praatio import textgrid
from scipy.signal import find_peaks

def extractInfosFromTier(Tier):
    xmi = []
    xma = []
    lab = []

    for start, end, label in Tier.entries:
        xmi.append(start)
        xma.append(end)
        lab.append(label)
    return xmi, xma, lab

fs, audio_signal = read("TP2/Grp5/S13-PWS/PeriodicAlong/S13_0009-BaT.wav")
bips = audio_signal[:,0]
taps = audio_signal[:,1]

tg = textgrid.openTextgrid("TP2/Grp5/S13-PWS/PeriodicAlong/S13_0009-BaT.TextGrid", False)
xmin,xmax,label = extractInfosFromTier(tg.getTier(tg.tierNames[0]))

tpeaks_bips = find_peaks(bips[int(xmin[0]*fs):int(xmax[0]*fs)],
                         height=0.2,
                         distance=0.5*fs)[0]
tpeaks_taps = find_peaks(taps)
print(tpeaks_bips)