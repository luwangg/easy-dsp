import sys
import numpy as np

import browserinterface
import algorithms as rt

"""
Number of snapshots for DOA will be: ~2*buffer_size/nfft
"""
buffer_size = 8192
nfft = 512
num_angles = 60

"""
Read hardware config from file
"""
try:
    import json
    with open('./hardware_config.json', 'r') as config_file:
        config = json.load(config_file)
        config_file.close()
    sampling_freq = config['sampling_frequency']
    array_type = config['array_type']
    led_ring_address = config['led_ring_address']
except:
    # default when no hw config file is present
    sampling_freq = 44100
    array_type = 'random'
    led_ring_address = '/dev/cu.usbmodem1421'

"""Select appropriate microphone array"""
if array_type == 'random':
    mic_array = rt.bbb_arrays.R_compactsix_random
elif array_type == 'circular':
    mic_array = rt.bbb_arrays.R_compactsix_circular_1

"""
Select frequency range
"""
n_bands = 20
freq_range = [1000., 3500.]
f_min = int(np.round(freq_range[0]/sampling_freq*nfft))
f_max = int(np.round(freq_range[1]/sampling_freq*nfft))
range_bins = np.arange(f_min, f_max+1)
use_bin = True

vrange = [1., 200.]

"""Check for LED Ring"""
try:
    import matplotlib.cm as cm
    led_ring = rt.neopixels.NeoPixels(usb_port=led_ring_address,
        colormap=cm.afmhot, vrange=vrange)
    print("LED ring ready to use!")
    num_pixels = led_ring.num_pixels
except:
    print("No LED ring available...")
    led_ring = False
    num_pixels = 60

# a Bell curve for visualization
sym_ind = np.concatenate((np.arange(0, 30), -np.arange(1,31)[::-1]))
bell = np.exp(-sym_ind**2. / 4.)
P = np.zeros(num_pixels, dtype=np.float)

"""Initialization block"""
def init(buffer_frames, rate, channels, volume):
    global doa

    doa_args = {
            'L': mic_array,
            'fs': rate,
            'nfft': nfft,
            'num_src': 2,
            'n_grid': num_angles,
            'max_four': 4,
            'max_ini': 10,
            'max_iter': 3,
            'G_iter': 1,
            'low_rank_cleaning': True,
            'signal_type': 'visibility',
            }

    doa = rt.doa.FRIDA(**doa_args)

"""Callback"""
def apply_doa(audio):
    global doa, nfft, buffer_size, led_ring

    if (audio.shape[0] != browserinterface.buffer_frames 
        or audio.shape[1] != browserinterface.channels):
        print("Did not receive expected audio!")
        return

    # compute frequency domain snapshots
    hop_size = int(nfft/2)
    n_snapshots = int(np.floor(buffer_size/hop_size))-1
    X_stft = rt.utils.compute_snapshot_spec(audio, nfft, 
        n_snapshots, hop_size)

    # pick bands with most energy and perform DOA
    if use_bin:
        bands_pwr = np.mean(np.sum(np.abs(X_stft[:,range_bins,:])**2, axis=0), axis=1)
        freq_bins = np.argsort(bands_pwr)[-n_bands:] + f_min
        doa.locate_sources(X_stft, freq_bins=freq_bins)
    else:
        doa.locate_sources(X_stft, freq_range=freq_range)

    # send to browser for visualization
    # Now map the angles to some function
    P[:] = 0
    for azimuth, power in zip(doa.azimuth_recon, doa.alpha_recon):
        i = int(round(num_pixels * azimuth / (2 * np.pi)))
        sigma = np.mean(power)
        P[i:] += bell[:num_pixels-i] * sigma
        P[:i] += bell[num_pixels-i:] * sigma

    to_send = ((P - vrange[0]) / (vrange[1] - vrange[0]) + 0.05).tolist()
    to_send.append(to_send[0])
    polar_chart.send_data([{ 'replace': to_send }])

    # send to lights if available
    if led_ring:
        led_ring.lightify(vals=P, realtime=True)

"""Interface features"""
browserinterface.register_when_new_config(init)
browserinterface.register_handle_data(apply_doa)

polar_chart = browserinterface.add_handler(name="Directions", 
    type='base:polar:line', 
    parameters={'title': 'Direction', 'series': ['Intensity'], 
    'numPoints': num_angles} )

"""START"""
browserinterface.start()
browserinterface.change_config(channels=6, buffer_frames=buffer_size,
    rate=sampling_freq, volume=80)
browserinterface.loop_callbacks()