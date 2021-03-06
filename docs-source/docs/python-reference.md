# Intro

This part explains how to get the audio streams in Python code and how to send results to the webapp, so it can display them in live.

## How it works

When you write code in the webapp editor and click "Execute", it will be executed as a new Python script.
So either you use the browser or write directly a Python script that you launch from your terminal, the way it works is similar.

To easily access the audio streams, and display something in the webapp, we provide a Python module `browserinterface`.

The minimum Python code is the following:

```python
# First you import the module
import browserinterface

# Then you define the function that will perform some algorithm on the audio streams
def handle(buffer):
    print "Buffer received", len(buffer)


# Finally you register your function, so browserinterface will call it every time a new audio buffer is received,
browserinterface.register_handle_data(handle)
# You start the module, so it will connects to WSAudio, and listen so the browser will be able to connect
browserinterface.start()

# Finally you start the callbacks blocking infinite loop
# All code below will not be executed
# This mecanism ensures the callbacks you specified are called from the main thread
# If you forget this call, your callbacks will never be called!
browserinterface.loop_callbacks()
```

In the following, when we talk about functions and variables, they all come from the module `browserinterface`, so you must prefix them with `browserinterface.`.


## If the browser is not needed

If you run your own Python script and don't need the browser (to display the output), you have to set the variable `inform_browser` to false.
In that case, you also have to specify the IP address of the board, using the variable `board_ip` (when you use the browser, it directly communicate to your script the IP address of the board, so you don't need to specify it).

```python
browserinterface.inform_browser = False
browserinterface.board_ip = '10.1.2.3'
```

This must be done at the very beginning, before you `start()` the module.


## Reading the configuration

Four variables contain the configuration:

* `rate`: the rate in bits/second;
* `channels`: the number of channels;
* `buffer_frames`: the number of audio frames contained in one buffer;
* `volume`: the volume between 0 and 100.

These are read-only, and you must not change them.


## Receiving configuration changes

When you start your script, the four previous variables will still be uninitialized, because the module did not received the configuration yet.
Plus, sometimes, a configuration change can happen.

You can register a callback to receive the configuration, when it first arrives, and each time it changes, using `register_when_new_config(callback)`.
Your callback function must accept four parameters: `callback(buffer_frames, rate, channels, volume)`.

If you have some variables to initialize, depending on the audio configuration, **it is safer to do it in your callback**.

```python
def my_function(buffer_frames, rate, channels, volume):
    print "New config received: buffer_frames, rate, channels, volume"
    print buffer_frames, rate, channels, volume

browserinterface.register_when_new_config(my_function)
```


## Changing the configuration

You can change the configuration using the method `change_config(rate, channels, buffer_frames, volume)`.

```python
browserinterface.change_config(rate=44100, channels=2, buffer_frames=2048, volume=90)
```


## Receiving the audio streams

You can define a function that will be called each time a new audio buffer is received, by registering it:
```python
def my_function(buffer):
    print "Buffer received", len(buffer)
browserinterface.register_handle_data(my_function)
```

The parameter `buffer` will contain a 2D numpy array of size `(buffer_frames, channels)` containing 16 bits integers (between -32 767 and +32 767).

An example with 5 frames per buffer and 2 channels:

```python
np.array([
  [100, 300],
  [80, 240],
  [130, 0],
  [-800, 123],
  [-400, 0]
], dtype=np.int16)
```


## Recording audio

You can ask the Python module to record a certain audio duration for you, and to call the callback you specified, using the method `record_audio(duration, callback)` with `duration` in milliseconds.
The recording starts just after you called the method.

The function `callback` you specified must accept one parameter `buffer` (which will follow the same structure than above).
Pay attention that `buffer` will not be exactly of the duration you specified, but can be slightly longer.

```python
def my_function(buffer):
    print "Audio has been recorded", len(buffer)

browserinterface.record_audio(5000, my_function) # my_function will be called after 5 seconds
browserinterface.record_audio(15000, my_function) # my_function will be called after 15 seconds
```


## Sending audio

It is possible to send a new audio stream to the browser so it will play it.
The configuration must be exactly the same as the input buffer (same number of channels, same rate, same number of frames per buffer).

The method `send_audio(buffer)` accepts a 2D Numpy array, following the same format as the input.


## Using the data handlers

After you performed some algorithms on the audio streams, you may want to display some outputs, like charts, histograms or new audio streams.
What you have to do is to send the data you want to display to a **data handler** of the webapp.
You have two simple steps to do:

1. You create a new data handler using the function `add_handler(name, type, parameters)` which returns an object representing this new instance;
2. You send data to this instance using its method `send_data(data)`.

Once you call the function `add_handler`, a new tab will be created in the webapp, with the name `name` you specified, and the chart/plot/audio player will appear inside.
You can use the part [Data Handlers](data-handlers.md) to see which *types* of data handlers exist, which parameters are supported, and which structure the `data` you send must follow.
