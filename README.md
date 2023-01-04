# xrandr-brightness

A console application for adjusting the brightness of three monitors (for Ubuntu).

Before the first launch, configure the names of your monitor adapters in the `adapters` dictionary (about the 22nd line of the script:)

Example
```
# Configure your adapters here. The connected adapters can be found using the command
# xrandr --prop | grep connected
# If you have only two monitors, you can delete place.Middle of adapters
adapters = {PLACE.Left:'DP-1',
            PLACE.Middle: 'HDMI-1',
            PLACE.Right: 'DVI-D-1-1'}
```
To search for connected monitors, you can use the command
`xrandr --prop | grep connected`

Control:
_Up arrow_, _down arrow_ - select the monitor whose brightness will change.
_Down arrow_ also selects all monitors at the same time to change the brightness.
_Left arrow_, _right arrow_ - brightness change.
_Space bar_ - apply the set brightness without changing. This is for the case when the brightness of the monitor has changed under the influence of external reasons.
_q_ - exit with the settings saved. The next time you start, these settings will be applied automatically. The settings are also saved when the terminal window is closed.

