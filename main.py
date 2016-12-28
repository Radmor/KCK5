from __future__ import division
from numpy.fft import rfft
from numpy import argmax, mean, diff, log
from matplotlib.mlab import find
from scipy.signal import blackmanharris, fftconvolve
from time import time
import sys
import math
import numpy
import random
import struct
import wave
from os import listdir, path
datadir = 'train'
WINDOWSIZE = 512



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

def autocorrelation(file, frequency, windowsize):
    waves, framerate = file

    dt = 1/frequency

    offset = math.floor(framerate * dt)
    corr = numpy.correlate(numpy.array(waves[0:windowsize]), numpy.array(waves[offset:offset+windowsize]))
    corr =  numpy.corrcoef(numpy.array([waves[0:windowsize], waves[offset:offset+windowsize]]))
    return 0 if numpy.isnan(corr[0][1]) else corr[0][1]

def classify_file(file, woman_frequency, man_frequency):
    windowsize = WINDOWSIZE

    woman_corr = autocorrelation(file, woman_frequency, windowsize)
    man_corr = autocorrelation(file, man_frequency, windowsize)

    if man_corr>woman_corr:
        return 'M'
    elif woman_corr>man_corr:
        return 'K'
    else:
        return random.choice(['M', 'K'])

    return 'M' if man_corr>=woman_corr else 'K'

def classify_files(files, woman_frequency, man_frequency):
    return [classify_file(file, woman_frequency, man_frequency) for file in files]

def compute_accuracy(classifications, answers):
    return sum([1 if classiffication==answer else 0 for classiffication, answer in zip(classifications,answers)])/len(answers)

def perform_computations(files):
    woman_min_freq = 50
    woman_max_freq = 300

    man_min_freq = 50
    man_max_freq = 300

    step = 10

    accuracy = []

    for woman_freq in range(woman_min_freq, woman_max_freq, step):
        for man_freq in range(man_min_freq, man_max_freq, step):
            classif = classify_files(files, woman_freq, man_freq)
            accuracy.append(compute_accuracy(classif, get_voices_sex(datadir)))

    return numpy.array(accuracy).reshape(len(range(woman_min_freq, woman_max_freq, step)), len(range(man_min_freq, man_max_freq, step)) )


data = input_files(datadir)

classif = classify_files(data, 190, 120)

out = perform_computations(data)
print(numpy.amax(out))
numpy.savetxt('out.txt', out)
# frequencies = calculate_frequencies(data)

# division_value, max_efficiency = automated_division(frequencies)
# print(division_value, max_efficiency)