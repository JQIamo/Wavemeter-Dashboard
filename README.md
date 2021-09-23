# Sr Lab Wavemeter Monitor

It is designed to work with the wave meter, fiber switch and DAC Arduino box in
Sr Lab.

Some cool features:
- A nice dashboard view to let you monitor the frequency and some crucial data
of several channels.
- PID (well, actually no D, just PI) control to set the DAC to fight against
frequency error.
- Signal channel display to let you have a clear view of the wave meter pattern,
long-term frequency changes, etc.
- Alert system, screaming at you if things went wrong.

## Screenshot

![Dashboard View](wavemeter_dashboard/docs/dashboard_view_screenshot.png)

![Single Channel View](wavemeter_dashboard/docs/single_channel_view_screenshot.png)

## Usage

1. Dependencies `pyqt5`, `numpy`, `scipy`, `pyqtgraph` should be installed in
advance.
2. Modified `config.json` to set the correct COM port of each device.
3. Run `main.py` with python.

## Docs

A introduction that briefly goes through the structure of this program can be 
found [here](wavemeter_dashboard/docs/README.md).


## TODO

### Planned
- [ ] main window: icon
- [ ] misc: wrap the whole program with `setup.py`.

### Good to have
- [ ] thumbnail: scroll zoom in/out
