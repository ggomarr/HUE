# Realtime sound spectrograph built with Python, PyAudio, NumPy and OpenCV
# Cosmin Gorgovan <cosmin AT linux-geek.org>, Apr 16 2011
# Released into the public domain by the copyright holder

# Reformatted by GGA, Jan 21, 2016

import pyaudio
import numpy
import cv

# No. of input samples used for a single FFT
CHUNK_SIZE = 1024

# Sampling rate
RATE = 22050

# Spectrogram's width in pixels
WINDOW_WIDTH = 700

# Don't change. Spectrogram's height in pixels
HEIGHT = CHUNK_SIZE/2

p = pyaudio.PyAudio()

stream = p.open(format = pyaudio.paInt16,
                channels = 1,
                rate = RATE,
                input = True,
                frames_per_buffer = CHUNK_SIZE)


spectrogram = cv.CreateImage((WINDOW_WIDTH, HEIGHT), cv.IPL_DEPTH_16U, 1)
cv.Set(spectrogram, 0)

while (True):
    data = stream.read(CHUNK_SIZE)
    data = numpy.fromstring(data, 'int16')
    freq = numpy.fft.rfft(data)
    
    tmp = cv.CreateImage((WINDOW_WIDTH, HEIGHT), cv.IPL_DEPTH_16U, 1)
    
    # Copy last WIDTH-1 columns from spectogram to the first WIDTH-1 columns in tmp
    cv.SetImageROI(tmp, (0, 0, WINDOW_WIDTH-1, HEIGHT))
    cv.SetImageROI(spectrogram, (1, 0, WINDOW_WIDTH-1, HEIGHT))
    cv.Copy(spectrogram, tmp)
    cv.ResetImageROI(tmp)
    
    for i in range(1, CHUNK_SIZE/2):
        rvalue = abs(int(numpy.real(freq[i])))
      
        cv.Line(tmp, (WINDOW_WIDTH-1, HEIGHT-i), (WINDOW_WIDTH-1, HEIGHT-i),  rvalue)
        #freq = int(RATE * (max_index / float(chunk)))
    spectrogram = tmp
    
    cv.ShowImage("Spectograph", spectrogram)
    if (cv.WaitKey(10) == ord('q')):
        break
      
stream.stop_stream()
stream.close()
p.terminate()