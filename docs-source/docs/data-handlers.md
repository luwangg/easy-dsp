# Definition

A data handler is an object in the webapp which can be used to handle some data.

Typically, they are used to vizualise the output of the program written by the user, which takes into input the audio streams, and could want to draw some charts as a result.
Several data handlers come with the project, but you can also easily write your own, as explained.

There are two main steps when using a data handler:

1. You create it, with some configuration information;
2. You send data to it.

# Example

You can use the data handlers from your Python code (it is defined in more details in the Python part reference):

```python
import browserinterface
import time
import random

browserinterface.start()

# First, we create our handlers
# First we precise the name, then the type, and third the possible parameters
## A line chart, with two series
c1 = browserinterface.add_handler("First chart - Line", 'base:graph:line', {'xName': 'Name of x axis', 'series': [{'name': 'First serie'}, {'name': 'Second serie'}]})
## A plot chart, with one serie
c2 = browserinterface.add_handler("Second chart - Plot", 'base:graph:plot', {'xName': 'Name of super x axis', 'series': [{'name': 'Only serie'}]})
## A polar chart, with one serie
c3 = browserinterface.add_handler("Third chart - Polar", 'base:polar:area', {'title': 'Awesome polar chart', 'series': ['Intensity'], 'legend': {'from': 0, 'to': 360, 'step': 10}})

# Then we can send some data to the different handlers
c1.send_data({'add': [{'x': [1, 2, 3, 4], 'y': [89, 70, 40, 2, 3]}, {'x': [1, 2, 3, 4], 'y': [39, 20, -2, 4]}]})
c2.send_data({'add': [{'x': [10, 30, 40, 70], 'y': [100, 234, 90, 23]}]})

for i in range(5, 40):
  c1.send_data({'add': [{'x': [i], 'y': [20+i*5*random.random()]}, {'x': [i], 'y': [i*5*random.random()]}]})
  c3.send_data([{'append': (200+i*3)*10}])
  time.sleep(1)
```


## DataHandler: draw classic charts

This handler can be used to draw line charts, histograms.
There are always 2D charts, with an x axis and an y axis.

<img src="../img/handler-ex1.png" style="height: 100px !important;" />
<img src="../img/handler-ex2.png" style="height: 100px !important;" />
<img src="../img/handler-ex3.png" style="height: 100px !important;" />

### Types

* `base:graph:line`: a line chart;
* `base:graph:area`: an area chart;
* `base:graph:bar`: an histogram;
* `base:graph:plot`: a plot chart.

### Configuration

The following options are accepted during the creation:

* `xName` (string): name of the x axis;
* `series` (array[object]): parameters (name, color) of the different series. **This parameter fixes the number of series to display.** The object representing a serie can have the following keys:
    * `name` (string) [optional]: name of the serie;
    * `color` (string) [optional]: color for the serie. Can be a CSS name (`blue`, `red`, `steelblue`, `green`, `lightblue`...) or a rgba value (`rgba(192,132,255,0.3)`).
* `min` (number) [optional]: minimum value for y;
* `max` (number) [optional]: maximum value for y;
* Limit the number of points displayed. When the limit is reached, the first values are deleted, and all the graph is "translated":
    * `xLimitNb` (integer): maximum number of points to display.

### Sending data

#### Adding points

You can add new points to each series:

```json
{
  "add": [
    {
      "x": [3, 4],
      "y": [39, 21]
    },
    {
      "x": [3, 4],
      "y": [11, 32.5]
    }
  ]
}
```

The size of the array `add` must be the number of series (specified during the creation).

#### Replacing all the points

You can also replace all the points of all the series:

```json
{
  "replace": [
    {
      "x": [0, 1, 2, 3, 4],
      "y": [8, 1, 3, 0, 2]
    },
    {
      "x": [0, 1, 2, 3, 4],
      "y": [21, 18, 17, 13, 10]
    }
  ]
}
```


## DataHandler: draw polar charts

This handler can draw polar charts.

<img src="../img/handler-polar-ex2.png" style="height: 200px !important;" />
<img src="../img/handler-polar-ex1.png" style="height: 200px !important;" />

### Types

* `base:polar:line`: a line polar chart;
* `base:polar:area`: an area polar chart.

### Configuration

The following options are accepted during the creation:

* `title` (string): name of the chart;
* `series` (array[string]): names of the different series. **This parameter fixes the number of series to display**;
* `legend` (object): defines the scale and contains the following parameters:
    * `from` (number): the value corresponding to a start from the north;
    * `to` (number): the value corresponding to the arrival to the north after one revolution;
    * `step` (number): the size of the subdivision.


### Sending data

#### Adding an entry

You can add new data to each serie:

```json
[
  {"append": 10},
  {"append": 4},
  {"append": 43}
]
```

The new values will be pushed at the end of previous data of each serie.
The size of the array must be the number of series (specified during the creation).


#### Replacing all entries

You can replace all data at once:

```json
[
  {"replace": [3, 5, 1, 1, 4]},
  {"replace": [1, 7, 3.4, 2.2, 2]},
  {"replace": [2, 1, 3.8, 3.9, 4]}
]
```

The size of the array must be the number of series (specified during the creation).


## DataHandler: draw heatmaps

This handler can draw heatmaps.

<img src="../img/handler-heatmap-ex1.png" style="display: block; height: 200px !important; margin: 0 auto;" />

### Types

* `base:heatmap`: a heatmap.

### Configuration

The following options are accepted during the creation:

* `min` (number): the value corresponding to the minimum (which will be blue);
* `max` (number): the value corresponding to the maximum (which will be red).

### Sending data

#### Replacing all entries

You can replace all data at once by sending a 2D-array.
Each array corresponds to a row and contains numbers.

```js
[
  [2, 3, 4, 0], // first row of the image
  [1, 0, 0, 1], // second row of the image
  [3, 4, 4, 1], // last row of the image
]
```


## Write your own data handler

From a code point of view, a data handler is a class, from which instances are created on demand.
Because we are talking about JavaScript, we are not working with a real class, but with a function returning an object.

### Defining your data handler

When instantiated, two parameters will be given to your function:
* the html element you can use to display things;
* the `parameters` object specified by the user.

Your function must return an objet with a property/method `newData` that will be called with the `data` object specified by the user.

```js
function myDataHandler(html, parameters) {
  // html is the DOM element you can use
  // Here we just append to this html element the parameters object
  $(html).append(JSON.stringify(parameters) + '<br />');

  // We must return an object with a method newData
  return {
    newData: function (data) {
      // This code will be executed each time data is sent to this data handler
      $(html).append(JSON.stringify(data) + '<br />');
    }
  }
}
```

### Registering your data handler

Then, you have to choose a type for your data handler and to register it:

```js
dataHandlers.registerNewType('customtype', myDataHandler);
```

The data handler can be registered by adding the above line to the file `js/myHandlers.js`.

### Using it

You can use it from the Python code like any other data handler:

```python
import browserinterface
myHandlerInstance = browserinterface.add_handler("Custom thing", 'customtype', {'param1': True, 'param2': 'hello', 'param3': [0, 1, 2]})
myHandlerInstance.send_data({'newData': {'i': i}})
myHandlerInstance.send_data(['an', 'array', 'this', 'time'])
```
