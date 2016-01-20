'''
Created on Jan 15, 2016

@author: ggomarr
'''

import parameters.all_conf as param
import beautifulhue.api
import pyaudio
import numpy
import matplotlib.pyplot
import matplotlib.image
import datetime
    
class discotheque:
    '''
    Set up a hue light controller and methods to:
    - Listen to sound captured on the mic (or rerouted to it from the speakers using the PulseAudio Volume Control pannel)
    - Convert sound features (volume and frequency) into color and brightness
    - Update the state of the hue lamps
    ''' 

    def __init__(self,light_id=param.light_id):
        self.light_id=light_id
        self.mem_volume=numpy.ones(len(param.mem_weights))
        self.brightness=self.volume_to_brightness(self.mem_volume)
        self.mem_freqs=numpy.ones((len(param.col_verts),len(param.mem_weights)))
        self.color=self.freqs_to_color(self.mem_freqs)
               
    def signal_to_volume(self,signal):
        return numpy.sqrt(numpy.mean(numpy.square(signal.astype('int32'))))

    def update_mem_volume(self,volume):
        self.mem_volume=numpy.roll(self.mem_volume,-1)
        self.mem_volume[-1]=volume
    
    def volume_to_brightness(self,mem_volume):
        return int(param.max_brightness*numpy.dot(param.mem_weights,mem_volume)/max(self.mem_volume))

    def signal_to_freqs(self,signal):
        freq=numpy.fft.rfft(signal)
        return [ numpy.sqrt(sum(numpy.square(abs(freq[freqbin[0]:freqbin[1]]))))
                 for freqbin in param.freqbins ]

    def update_mem_freqs(self,freqs):
        self.mem_freqs=numpy.roll(self.mem_freqs,-1)
        self.mem_freqs[:,-1]=freqs

    def freqs_to_color(self,mem_freqs):
        freqbands=numpy.sum(numpy.multiply(param.mem_weights,mem_freqs),1)
        if sum(freqbands)>0:
            freqbands=freqbands*param.col_bias
            aux_bias=[ param.winner_takes_all_bias[v] for v in numpy.argsort(freqbands) ]
            weights=freqbands*aux_bias
        else:
            weights=[1]*len(param.col_verts)*param.col_bias
        weights=[ 1.0*w/sum(weights) for w in weights ]
        return list(numpy.dot(weights,param.col_verts))

    def color_to_png(self,xy):
        return [ int(param.delta_s[0]*xy[0]+param.delta_0[0]),
                 int(param.delta_s[1]*xy[1]+param.delta_0[1]) ]

    def prepare_audio(self):
        return pyaudio.PyAudio().open(format = pyaudio.paInt16,
                                      channels = 1,
                                      rate = param.sampling_rate,
                                      input = True,
                                      frames_per_buffer = param.chunk_size)

    def grab_signal(self):
        self.stream.start_stream()
        signal=numpy.fromstring(self.stream.read(param.chunk_size),'int16')
        self.stream.stop_stream()
        return signal

    def prepare_picture(self):
        fig=matplotlib.pyplot.figure()
        graph=fig.add_subplot(111)
        graph.imshow(matplotlib.image.imread(param.bkg_img))
        fig.gca().set_autoscale_on(False)
        fig.show()
        return fig, graph

    def update_picture(self):
        pt=self.color_to_png(self.color)
        self.graph.plot([ pt[0] ], [ pt[1] ], 'ro')
        self.fig.show()
        matplotlib.pyplot.pause(0.000001)
        self.graph.lines[0].remove()

    def prepare_lights(self):
        bridge=beautifulhue.api.Bridge(device={'ip':param.ip}, user={'name':param.username})
        bridge.light.update({'which':self.light_id,
                             'data':{'state':{'on':True,
                                              'xy':self.color,
                                              'bri':self.brightness,
                                              'transitiontime':0}}})
        return bridge

    def update_lights(self):
        self.bridge.light.update({'which':self.light_id,
                                  'data':{'state':{'xy':self.color,
                                                   'bri':self.brightness,
                                                   'transitiontime':0}}})

    def prepare_log(self):
        return open(param.log_name+datetime.datetime.now().strftime("%Y%m%d%H%M%S"),'w')
    
    def update_log(self):
        self.log.write('{}, {}, {}, {}\n'.format(self.mem_volume[-1],self.brightness,self.mem_freqs[:,-1],self.color))

    def clean_up(self):
        self.stream.stop_stream()
        self.stream.close()
        self.log.close()

if __name__ == "__main__":
    disco=discotheque()
    disco.bridge=disco.prepare_lights()
    disco.stream=disco.prepare_audio()
    disco.fig, disco.graph=disco.prepare_picture()
    disco.log=disco.prepare_log()
    try:
        while True:
            signal=disco.grab_signal()
            disco.update_mem_volume(disco.signal_to_volume(signal))
            disco.update_mem_freqs(disco.signal_to_freqs(signal))
            disco.brightness=disco.volume_to_brightness(disco.mem_volume)
            disco.color=disco.freqs_to_color(disco.mem_freqs)
            disco.update_lights()
            disco.update_picture()
            disco.update_log()
    except KeyboardInterrupt:
        pass
    disco.clean_up()