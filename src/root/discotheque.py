'''
Created on Jan 15, 2016

@author: ggomarr
'''

import parameters.all_conf as param
import beautifulhue.api
import pyaudio
import numpy, scipy.stats
import matplotlib.pyplot
import matplotlib.image
import datetime, time

class discotheque:
    '''
    Set up a hue light controller and methods to:
    - Listen to sound captured on the mic (or rerouted to it from the speakers using the PulseAudio Volume Control pannel)
    - Convert sound features (volume and frequency) into color and brightness
    - Update the state of the hue lamps
    ''' 

    def __init__(self,light_id=param.light_id,normalize_signal_to_color=True):
        self.light_id=light_id
        self.brightness=param.init_brightness
        self.color=numpy.array(param.init_color)
        self.delta_brightness=0
        self.delta_color=numpy.array([0,0])
        if normalize_signal_to_color:
            self.signal_to_color=self.signal_to_color_normalized
            self.mem_freqs=numpy.zeros([len(param.bin_fracs),param.mem_length])
        else:
            self.signal_to_color=self.signal_to_color_absolute
               
    def signal_to_brightness(self,signal):
        self.volume=numpy.sqrt(numpy.mean(numpy.square(signal.astype('int32'))))
        target_brightness=param.brightness_scale*self.volume
        self.delta_brightness=param.inertia*self.delta_brightness+param.sluggishness*(target_brightness-self.brightness)
        self.brightness=int(self.brightness+self.delta_brightness)

    def signal_to_color_normalized(self,signal):
        freq=numpy.fft.rfft(signal)
        self.freqs= [ numpy.sqrt(sum(numpy.square(abs(freq[freq_bin[0]:freq_bin[1]]))))
                      for freq_bin in param.freq_bins_fft ]
        if sum(self.freqs)>0:
            self.mem_freqs=numpy.roll(self.mem_freqs,-1,1)
            self.mem_freqs[:,-1]=self.freqs
            aux_means=numpy.mean(self.mem_freqs,1)
            aux_stds=numpy.std(self.mem_freqs,1)
            freqs=[ scipy.stats.norm(aux_means[i],aux_stds[i]).cdf(self.freqs[i]) for i in range(len(param.bin_fracs)) ]
            aux_bias=[ param.winner_takes_all[v] for v in numpy.argsort(freqs) ]
            weights=numpy.multiply(freqs,aux_bias)            
        else:
            weights=[1]*len(param.col_verts)
        weights=[ 1.0*w/sum(weights) for w in weights ]
        target_color=numpy.dot(weights,param.col_verts)
        self.delta_color=param.inertia*self.delta_color+param.sluggishness*(target_color-self.color)
        self.color=self.color+self.delta_color

    def signal_to_color_absolute(self,signal):
        freq=numpy.fft.rfft(signal)
        self.freqs= [ numpy.sqrt(sum(numpy.square(abs(freq[freq_bin[0]:freq_bin[1]]))))
                      for freq_bin in param.freq_bins_fft ]
        if sum(self.freqs)>0:
            freqs=numpy.subtract(self.freqs,param.freq_const)
            freqs=numpy.multiply(freqs,param.freq_slope)
            aux_bias=[ param.winner_takes_all[v] for v in numpy.argsort(freqs) ]
            weights=numpy.multiply(freqs,aux_bias)
        else:
            weights=[1]*len(param.col_verts)
        weights=[ 1.0*w/sum(weights) for w in weights ]
        target_color=numpy.dot(weights,param.col_verts)
        self.delta_color=param.inertia*self.delta_color+param.sluggishness*(target_color-self.color)
        self.color=self.color+self.delta_color

    def color_to_png(self,xy):
        return [ int(param.delta_s[0]*xy[0]+param.delta_0[0]),
                 int(param.delta_s[1]*xy[1]+param.delta_0[1]) ]

    def prepare_audio(self):
        self.stream=pyaudio.PyAudio().open(format = pyaudio.paInt16,
                                           channels = 1,
                                           rate = param.sampling_rate,
                                           input = True,
                                           frames_per_buffer = param.chunk_size)

    def grab_signal(self):
        self.stream.start_stream()
        signal=numpy.fromstring(self.stream.read(param.chunk_size),'int16')
        self.stream.stop_stream()
        return signal

    def prepare_picture_color(self):
        self.fig_color=matplotlib.pyplot.figure()
        self.graph_color=self.fig_color.add_subplot(111)
        self.graph_color.imshow(matplotlib.image.imread(param.bkg_img))
        self.graph_color.autoscale(False)
        self.fig_color.show()

    def update_picture_color(self):
        if self.graph_color.lines:
            self.graph_color.lines[-1].remove()
        pt=self.color_to_png(self.color)
        self.graph_color.plot([ pt[0] ], [ pt[1] ], 'ro')
        self.fig_color.show()
        matplotlib.pyplot.pause(0.000001)

    def prepare_picture_freqs(self):
        self.fig_freqs=matplotlib.pyplot.figure()
        self.graph_freqs=self.fig_freqs.add_subplot(111)
        self.graph_freqs.axis([0,param.sampling_rate/2,0,param.max_band_val])
        self.graph_freqs.autoscale(False)
        for freq_bin in param.freq_bin_freqs:
            for freq_bin_freq in freq_bin:
                self.graph_freqs.axvline(freq_bin_freq,0,1)
        self.fig_freqs.show()

    def update_picture_freqs(self):
        if self.graph_freqs.lines:
            self.graph_freqs.lines[-1].remove()
        ptx=[ int((freq_bin[0]+freq_bin[1])/2) for freq_bin in param.freq_bin_freqs ]
        pty=self.freqs
        self.graph_freqs.plot(ptx, pty, 'ro')
        self.fig_freqs.show()
        matplotlib.pyplot.pause(0.000001)

    def prepare_lights(self):
        self.bridge=beautifulhue.api.Bridge(device={'ip':param.ip}, user={'name':param.username})
        self.bridge.light.update({'which':self.light_id,
                                  'data':{'state':{'on':True,
                                                   'xy':list(self.color),
                                                   'bri':self.brightness,
                                                   'transitiontime':int(param.adjust_every*10)}}})

    def update_lights(self):
        self.bridge.light.update({'which':self.light_id,
                                  'data':{'state':{'xy':list(self.color),
                                                   'bri':self.brightness,
                                                   'transitiontime':int(param.adjust_every*10)}}})

    def prepare_log(self):
        self.log=open(param.log_name+datetime.datetime.now().strftime("%Y%m%d%H%M%S"),'w')
        self.log.write('Volume, Brightness, Delta_brightness, Freqs, Color, Delta_color\n')
    
    def update_log(self):
        self.log.write('{}, {}, {}, {}, {}, {}\n'.format(self.volume,self.brightness,self.delta_brightness,self.freqs,self.color,self.delta_color))

    def wait(self,adjust_every=param.adjust_every):
        time.sleep(adjust_every)
        
    def clean_up(self):
        self.stream.stop_stream()
        self.stream.close()
        self.log.close()

def continuous_pyaudio_listener():
    p = pyaudio.PyAudio()
    stream = p.open(format = pyaudio.paInt16,
                    channels = 1,
                    rate = 22050,
                    input = True,
                    frames_per_buffer = 1024)
    try:
        while True:
            stream.read(1024)
    except KeyboardInterrupt:
        pass        
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    disco=discotheque(normalize_signal_to_color=False)
    disco.prepare_lights()
    disco.prepare_audio()
    disco.prepare_picture_color()
    disco.prepare_picture_freqs()
    disco.prepare_log()
    try:
        while True:
            signal=disco.grab_signal()
            disco.signal_to_brightness(signal)
            disco.signal_to_color(signal)
            disco.update_lights()
            disco.update_picture_color()
            disco.update_picture_freqs()
            disco.update_log()
            disco.wait(param.adjust_every)
    except KeyboardInterrupt:
        pass
    disco.clean_up()

