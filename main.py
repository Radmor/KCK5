from __future__ import division
from numpy.fft import rfft
from numpy import argmax, mean, diff, log
from matplotlib.mlab import find
from scipy.signal import blackmanharris, fftconvolve
from time import time
import sys
import math


import struct
import wave
from os import listdir, path
datadir = 'train'





def parabolic(f, x):
    """Quadratic interpolation for estimating the true position of an
    inter-sample maximum when nearby samples are known.

    f is a vector and x is an index for that vector.

    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
    through point x and its two neighbors.

    Example:
    Defining a vector f with a local maximum at index 3 (= 6), find local
    maximum if points 2, 3, and 4 actually defined a parabola.

    In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]

    In [4]: parabolic(f, argmax(f))
    Out[4]: (3.2142857142857144, 6.1607142857142856)

    """
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)


def autocorr(sig, fs):
    """
    Estimate frequency using autocorrelation
    """
    # Calculate autocorrelation (same thing as convolution, but with
    # one input reversed in time), and throw away the negative lags
    corr = fftconvolve(sig, sig[::-1], mode='full')
    corr = corr[len(corr)//2:]

    # Find the first low point
    d = diff(corr)
    start = find(d > 0)[0]

    # Find the next peak after the low point (other than 0 lag).  This bit is
    # not reliable for long signals, due to the desired peak occurring between
    # samples, and other peaks appearing higher.
    # Should use a weighting function to de-emphasize the peaks at longer lags.
    peak = argmax(corr[start:]) + start
    px, py = parabolic(corr, peak)

    return fs / px

def calculate_frequencies(data):
    return [autocorr(out, framerate) for out, framerate in data]


def input_file(filepath):
    """ Funkcja wczytująca plik wav o podanej w parametrze ścieżce"""
    filepath = path.join(datadir,filepath)
    wav = wave.open(filepath, "r")
    (nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams ()
    frames = wav.readframes(nframes * nchannels)
    out = struct.unpack_from("%dh" % nframes * nchannels, frames)

    return (out,framerate)

def input_files(datadir):
    """ Funkcja wczytujaca po kolei wszystkie pliki w folderze okreslonym
    przez parametr funkcji"""
    return [input_file(filepath) for filepath in listdir(datadir)]

def get_voices_sex(datadir):
    return ['K' if 'K' in filepath else 'M' for filepath in listdir(datadir)]

def get_recordings_amount(datadir):
    return len(listdir(datadir))

def automated_division(frequencies):
    minvalue = min(frequencies)

    maxvalue = max(frequencies)
    voices_sex = get_voices_sex(datadir)

    print(maxvalue)
    print(voices_sex)
    recordings_amount = get_recordings_amount(datadir)

    max_efficiency = 0

    final_division_value = minvalue

    for division_value in range(math.floor(minvalue), math.floor(maxvalue)):
        counter = 0
        for frequency, voice_sex in zip(frequencies,voices_sex):
            temp_sex = 'M' if frequency<=division_value else 'K'
            counter += 1 if temp_sex==voice_sex else 0

        efficiency = counter/recordings_amount
        # print(counter)
        if efficiency > max_efficiency:
            max_efficiency = efficiency
            final_division_value = division_value

    return (final_division_value, max_efficiency)


data = input_files(datadir)
frequencies = calculate_frequencies(data)

division_value, max_efficiency = automated_division(frequencies)
print(division_value, max_efficiency)