import numpy as np

import browserinterface
import realtimeaudio as rt
import time


""" Select algorithm """
doa_algo = 'SRPPHAT'
doa_algo = 'FRI'
doa_algo = 'TOPS'
doa_algo = 'CSSM'
doa_algo = 'WAVES'
doa_algo = 'MUSIC'
doa_algo_config = dict(
        MUSIC=dict(vrange=[0.2, 0.6]),
        SRPPHAT=dict(vrange=[0.1, 0.4]),
        FRI=dict(vrange=[0., 1.]),
        )

"""Select appropriate microphone array"""
mic_array = rt.bbb_arrays.R_compactsix_random; sampling_freq = 44100
# mic_array = rt.bbb_arrays.R_compactsix_circular_1; sampling_freq = 48000

"""
Parameters
"""
nfft = 1024         # impacts frequency resolution
n_snapshots = 25    # more snapshots typically yields better DOA estimate
num_angles = 360    # more angles typically yields better spatial resolution
n_frames = 10       # how many times to apply DOA

hop_size = int(nfft/2)                       # in number of sample
frame_length = (n_snapshots+1)*hop_size      # in number of sample
recording_duration = float(frame_length*n_frames)/sampling_freq   # in sec

"""Check for LED Ring"""
try:
    from neopixels import NeoPixels
    import matplotlib.cm as cm
    led_ring = NeoPixels(usb_port='/dev/cu.usbmodem1411',
        colormap=cm.afmhot)
    print("LED ring ready to use!")
except:
    print("No LED ring available...")
    led_ring = False

# create DOA object
doa_args = {
        'L': mic_array,
        'fs': sampling_freq,
        'nfft': nfft,
        'num_src': 1,
        'n_grid': num_angles
        }
# doa = rt.doa.SRP(**doa_args)
# doa = rt.doa.MUSIC(**doa_args)
# doa = rt.doa.CSSM(num_iter=1, **doa_args)
# doa = rt.doa.WAVES(num_iter=1, **doa_args)
doa = rt.doa.TOPS(**doa_args)
# doa = rt.doa.FRIDA(max_four=5, signal_type='visibility', G_iter=1, **doa_args)

# choose frequency range
n_bands = 5
freq_range = [100., 4500.]
f_min = int(np.round(freq_range[0]/sampling_freq*nfft))
f_max = int(np.round(freq_range[1]/sampling_freq*nfft))
range_bins = np.arange(f_min, f_max+1)


def apply_doa(audio):
    global doa

    for i in range(n_frames):

        signals = audio[frame_length*i:frame_length*(i+1),:]
        X_stft = rt.utils.compute_snapshot_spec(signals, nfft, n_snapshots, hop_size)

        if isinstance(doa, rt.doa.TOPS):
            print('Frequency range: {0}'.format(freq_range))
            doa.locate_sources(X_stft, freq_range=freq_range)
        else:
            bands_pwr = np.mean(np.sum(np.abs(X_stft[:,range_bins,:])**2, axis=0), axis=1)
            freq_bins = np.argsort(bands_pwr)[-n_bands:] + f_min
            freq_hz = np.array(freq_bins, dtype=np.float32)/nfft*sampling_freq
            print('Selected frequency bins: {0}'.format(freq_bins))
            print('Selected frequencies: {0} Hertz'.format(freq_hz))
            doa.locate_sources(X_stft, freq_bins=freq_bins)

        # send to browser for visualization
        if doa.grid.values.max() > 1:
            doa.grid.values /= doa.grid.values.max()
        to_send = doa.grid.values.tolist()
        to_send.append(to_send[0])
        polar_chart.send_data([{ 'replace': to_send }])

        # send to lights if available
        if led_ring:
            led_ring.lightify(vals=doa.grid.values, realtime=True)

        time.sleep(float(frame_length)/sampling_freq)
    

browserinterface.record_audio(recording_duration*1000, apply_doa)
polar_chart = browserinterface.add_handler(name="Directions", 
    type='base:polar:line', 
    parameters={'title': 'Direction', 'series': ['Intensity'], 
    'numPoints': num_angles} )

"""START"""
browserinterface.start()
browserinterface.change_config(buffer_frames=frame_length, channels=6, rate=sampling_freq, volume=80)
browserinterface.loop_callbacks()

