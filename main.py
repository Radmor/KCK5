import struct
import wave
from os import listdir
datadir = 'data'


def input_file(filepath):
	""" Funkcja wczytująca plik wav o podanej w parametrze ścieżce"""
	wav = wave.open(filepath, "r")
	(nchannels, sampwidth, framerate, nframes, comptype, compname) = wav.getparams ()
	frames = wav.readframes(nframes * nchannels)
	out = struct.unpack_from("%dh" % nframes * nchannels, frames)

	print(nchannels)


def input_files(datadir):
	""" Funkcja wczytujaca po kolei wszystkie pliki w folderze okreslonym 
	przez parametr funkcji"""
	for filepath in listdir(datadir):
		input_file(filepath)

input_files(datadir)
