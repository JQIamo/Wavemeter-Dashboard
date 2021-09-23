# Behind the screen

While designing this little piece of software, I tried my best to adhere to
the MVC (Model, View, Control) pattern, which is a common practice in developing
a interactive software. In short, the relation between M, V, C can be 
summarized as: View shows things of Model, Model hold things, Controller 
changes things in Model. It's not just a matter of formality. I have read and 
written many programs that have the controllers' function stuffed inside
models and things imploded miserably in the end (even this program was very
closed to becoming a victim in the middle), thus it is necessary to draw
the border properly. The usage of Qt greatly simplified the workflow and make 
doing decent MVC jobs not too much a pain.

When designing the interface, I made an attempt to mimic the design of the 
cockpit of an Airbus aeroplane. I use the font they designed for their flight
computer called [B612](https://b612-font.com/), which provides good legibility
and comfort of reading, and kept text in all caps. The attempt is largely
successful. The result is a professionally-looking interface that does it job
beautifully.

## Model

The only model in this program is the `ChannelModel` in `channel_model.py`. 
It wraps up all data and information of a channel, including intermediate 
parameters passing between different part of the program, therefore can be seen
as a _hub_ of communications. I did make some auxiliary tools, e.g.

 - a data structure that efficiently handles round-robin type of data (I call 
 it `longterm_data`, if you use the native wavemonitor monitoring program coming
 with HighFineness, you know what it means),

 - a set of pre-defined channel _alerts_ (in `channel_alert.py`, although not of
of these are alerts, some are just status information).

 But all in all, these components are all under the command of their master
 `ChannelModel`.
 
 A very important function of `ChannelModel` is: it serves as a _switch board_,
 it holds all the signals that are being triggered and listened by different 
 components. Basically, signals are the tools for some components to notice
 others _something has happened, you need to react_. 
 By avoiding straight-forward function-calls among modules with different
 roles but intercommunicate through subscribing to a signal and firing a signal,
 the modularity of controllers and views is gracefully preserved, and nothing is
 stitched together in ugly, dangerous ways.
 Major headaches that appears if one tries to cook up some naive version of
 Qt's signal system (warning, this would be very unwise!) would include 
 threads synchronizing, correctly dealing with discard objects that has signal 
 connect to it, etc. Qt's signal system has solution to almost all of these 
 headaches. Therefore it's not hard to understand why it's a good choice to let 
 Qt's mature signal system to handle all the hassles for you.
 
 For the parts that don't use signals to communicate, they must be nasty and I 
 shall be the culprit (they might be written at 11pm at night when I was not 
 completely sober), and should be tweaked with enough care. 
 
 **In one word, one should always refrain from directly
 calling function of a controller inside a view or vice versa, except under the
 case that it is absolutely necessary and safe to do so. Use signals as far as
 one can.**
 
 
 ## View
 
 Views are interesting. As you've seen, this little program has the so-called 
 _dashboard view_ and _single channel view_. Also, they are used under the
 wrapper called _main window_.
 
 Dashboard view comprises of `ChannelView`s. Each channel is represented by a
 row in the screen (I like to call them channel strip). The components (a.k.a.
 `widgets` in Qt's jargon) of each channel strip are stored in their 
 corresponding `ChannelView`s.
 It listens to a lot of signals that are fired when new data is available, and
 also fires signals when users interact with widgets to interact with
 controllers.
 
 Single channel view is much simpler. The way it used to painlessly handle
 different kinds of data is to invoke `GraphableDataProvider`, which provides
 a uniform interface of procuring data.
 
 A important little widget called `ChannelSetupWidget` was used in both views.
 It, as the name says, is the widget used to configure each channels. It
 generates `ChannelModel`s and pass them to views.
 
 One major challenge of building the user interface was _styling_. Since I
 decided to go with a cockpit design, I've lost the ease of using pre-baked Qt
 widget styling that comes right out of the box. I spent some time polishing
 each widget to make them look right. The result is a series of widgets in the
 `widgets/` folder (some come with special functions, not just styling), 
 cooperating with a stylesheet `style.qss`. They can be recycled in the future,
 when writing other program of this like.
 
 Another interesting fact to note is: in the dashboard view, the widget I used
 to display graphs is actually the `QChart`, which is the native Qt widget to
 display graphs. It doesn't have a huge amount of interactive components like
 `pyqtgraph`, but I think it should be faster, given the fact it is native to
 Qt. I used `pyqtgraph` in the single channel view. However, in the end, I don't
 really find `pyqtgraph` is slower, or `QChart` turns out to have a
 significant edge over `pyqtgraph`. A detailed profiling may help to tell the
 difference.
 
 
 ## Controller
 
 The data inside `ChannelModel` is controlled by `Monitor`, which does the real
 communication with the devices and fetches the data back. One fact worth noting:
 The monitoring process happens in another thread. The painting of the 
 user-interface and responding to users action is carried out in the Qt's 
 main-event-loop thread. Monitoring involves waiting for the response of the 
 device. Doing them inside the main thread will inevitably cause lags and even 
 freeze the whole program. But it also brings the whole can of worms of 
 multi-threading, like the common synchronization problems.
 
 The synchronization problems were amplified by the other controller, 
 `AlertTracker` which receives both the signals from users (main thread) and
 the monitoring thread. `AlertTracker` is used to keep track fo the status of
 the channel. A channel will _emit_ alerts during its life time, some of them
 are just status information like `QUEUED`, `MONITORING`, `PID ENGAGED`. 
 Sometimes things go south, that's when `OUT OF LOCK`, `UNDER EXPOSED` will
 appears and the channel strip starts to flashing. These functions rely on
 the `Monitor` emitting alert signals, the `AlertTracker` receiving signals,
 figuring out who is the most urgent one to display, and who is to be superseded
 by who, etc. It is actually the (logically) most complicated part of this 
 entire program and would be definitely reused by me in other programs in the 
 future.
 
 In Qt, signals are queued and executing in the main thread, but having two 
 threads emitting signals at the same moment could cause some confusion of the 
 order of the alert sequence. However, if monitoring thread itself messed up 
 the alert system, then it basically means things inside the `AlertTracker`
  is wrong, not some threading problems.