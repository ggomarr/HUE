'''
Created on Jan 15, 2016

@author: ggomarr
'''

import pyaudio
import numpy
import matplotlib
from parameters.all_conf import *

def grab_sample(chunk_size=512,sampling_rate=22050):
    import pyaudio
    import numpy
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,
                    channels = 1,
                    rate = sampling_rate,
                    input = True,
                    frames_per_buffer = chunk_size)
    data = stream.read(chunk_size)
    data = numpy.fromstring(data, 'int16')
    freq = numpy.fft.rfft(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    return freq, data

def show_color_map(my_x=[0,50,100,150],my_y=[0,50,100,150],wait_time=0.2,
                   bkg_img='/home/ggomarr/eclipse/workspace/Hue/000 Documentation/gamut_0.png'):
    import matplotlib.pyplot as mp_plt
    import matplotlib.image  as mp_img
    my_fig=mp_plt.figure()
    ax=my_fig.add_subplot(111)
    ax.imshow(mp_img.imread(bkg_img))
    my_fig.gca().set_autoscale_on(False)
    my_fig.show()
    for pt in range(len(my_x)):
        ax.plot([ my_x[pt] ], [ my_y[pt] ], 'ro')
        my_fig.show()
        mp_plt.pause(wait_time)
        ax.lines[0].remove()

def color_to_png(xy):
    # in_color_0=[0, 0], in_png_0=[73, 573]
    # in_color_1=[0.8,0.9], in_png_1=[530, 60]
    delta_0=[73,573]
    delta_s=[571.25, -570.0]
    return [ int(delta_s[0]*xy[0]+delta_0[0]), int(delta_s[1]*xy[1]+delta_0[1]) ] 

def bands_to_color(bands):
    if sum(bands)==0:
        bands=[1,1,1]
    bands=[ 1.0*b/sum(bands) for b in bands ]
    col_verts=[[0.15,0.1],[0.25,0.65],[0.65,0.3]]
    return [ col_verts[0][0]*bands[0]+col_verts[1][0]*bands[1]+col_verts[2][0]*bands[2],
             col_verts[0][1]*bands[0]+col_verts[1][1]*bands[1]+col_verts[2][1]*bands[2]]

def main():
    import pyaudio
    import numpy
    import matplotlib.pyplot as mp_plt
    import matplotlib.image  as mp_img

    # The FFT resulting from numpy.fft.rfft will have chunk_size/2 bins
    # and cover sampling_rate/2 Hz.
    # each bin being some sampling_rate/chunk_size wide
    # (please note bin 0 is 'different' because it is centered around 0 Hz)
    # The central frequencies of the bins can be computed with
    # numpy.fft.rfftfreq(chunk_size,1./sampling_rate)
    bin_fracs=[[0.0/3, 1.0/3],
               [1.0/3, 2.0/3],
               [2.0/3, 3.0/3]]
    bins=[[bin_fracs[0][0]*chunk_size/2, bin_fracs[0][1]*chunk_size/2],
          [bin_fracs[1][0]*chunk_size/2, bin_fracs[1][1]*chunk_size/2],
          [bin_fracs[2][0]*chunk_size/2, bin_fracs[2][1]*chunk_size/2]]
    bin_bias=[1,1,1]
    mem_profile=[0, 1, 2, 3, 4, 5]
    len_mem=len(mem_profile)
    mem=[0,bands_to_color([1,1,1])]*len_mem
    from beautifulhue.api import Bridge
    bridge = Bridge(device={'ip':'1.1.1.104'}, user={'name':'huepymaster'})
    light_id=3
    bkg_img='/home/ggomarr/eclipse/workspace/Hue/000 Documentation/gamut_0.png'
    my_fig=mp_plt.figure()
    ax=my_fig.add_subplot(111)
    ax.imshow(mp_img.imread(bkg_img))
    my_fig.gca().set_autoscale_on(False)
    my_fig.show()
    maxvol=1
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,
                    channels = 1,
                    rate = sampling_rate,
                    input = True,
                    frames_per_buffer = chunk_size)
    try:
        while True:
            data=stream.read(chunk_size)
            data=numpy.fromstring(data, 'int16')
            freq=numpy.fft.rfft(data)
            bands = [ sum(abs(freq[bins[0][0]:bins[0][1]]))*bin_bias[0],
                      sum(abs(freq[bins[1][0]:bins[1][1]]))*bin_bias[1],
                      sum(abs(freq[bins[2][0]:bins[2][1]]))*bin_bias[2] ]
            vol=sum(bands)
            if vol > maxvol:
                maxvol=vol
            brightness=int(vol/maxvol*255)
            xy=bands_to_color(bands)
            pt=color_to_png(xy)
            ax.plot([ pt[0] ], [ pt[1] ], 'ro')
            my_fig.show()
            mp_plt.pause(0.000001)
            ax.lines[0].remove()
            print (brightness,vol,xy,pt)
            resource = {
                        'which':light_id,
                        'data':{
                            'state':{'xy':xy, 'bri':brightness}
                        }
                    }
            bridge.light.update(resource)
    except KeyboardInterrupt:
        pass        

    stream.stop_stream()
    stream.close()
    p.terminate()

main()
