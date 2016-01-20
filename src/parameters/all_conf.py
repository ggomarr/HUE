# Hue bridge

ip='1.1.1.104'
username='huepymaster'
light_id=3
adjust_every=0.10

# Sound listener 

chunk_size = 1024
sampling_rate = 22050
    # The FFT resulting from numpy.fft.rfft will have chunk_size/2 bins
    # and cover sampling_rate/2 Hz.
    # each bin being some sampling_rate/chunk_size wide
    # (please note bin 0 is 'different' because it is centered around 0 Hz)
    # The central frequencies of the bins can be computed with
    # numpy.fft.rfftfreq(chunk_size,1./sampling_rate)
listen_every=0.05

# Rolling average

mem_profile=[ 1 ]*10
mem_weights=[ 1.0*v/sum(mem_profile) for v in mem_profile ]

# FTT to color converter

low_frac =[0.0, 0.2]
med_frac =[0.2, 0.6]
high_frac=[0.6, 1.0]

bin_fracs=[low_frac,med_frac,high_frac]

freqbins=[ [ v * chunk_size/2 for v in bin_frac ] for bin_frac in bin_fracs ]

winner_takes_all_bias=[1,1,10]

blue_vert=[0.15,0.1]
green_vert=[0.25,0.65]
red_vert=[0.65,0.3]

col_verts=[blue_vert,green_vert,red_vert]

col_bias=[1,10,10]

# Volume to brightness converter
max_brightness=255

# Color visualizer

bkg_img='/home/ggomarr/eclipse/workspace/Hue/000 Documentation/gamut_0.png'

in_color_0=[0, 0]
in_png_0=[73, 573]
in_color_1=[0.8,0.9]
in_png_1=[530, 60]

delta_0=[ v1-v0 for (v0, v1) in zip(in_color_0,in_png_0) ]
delta_s=[ (v1-v0)/(v3-v2) for (v0, v1, v2, v3) in zip(delta_0,in_png_1,in_color_0,in_color_1) ]

# Log file
log_name='/home/ggomarr/eclipse/workspace/Hue/000 Documentation/log.'