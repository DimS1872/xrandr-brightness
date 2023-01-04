import sys
import subprocess 
import enum
import curses
import json
import atexit
import signal


class PLACE (enum.IntEnum):
    """Placement of the monitor on the table"""
    Left = 1
    Middle = 2
    Right = 3
    ALL = 4

# TODO Identify adapters automatically and make the interface setup location at first startup

# Configure your adapters here. The connected adapters can be found using the command
# xrandr --prop | grep connected
# If you have only two monitors, you can delete place.Middle of adapters
adapters = {PLACE.Left:'DP-1',
            PLACE.Middle: 'HDMI-1',
            PLACE.Right: 'DVI-D-1-1'}

orderOfPlaces = []
currentPlaceIndex = 0

def setOrder():
    for place in [PLACE.Left, PLACE.Middle, PLACE.Right]:
        if place in adapters.keys():
            orderOfPlaces.append(place)
    orderOfPlaces.append(PLACE.ALL)

def nextPlace() -> PLACE:
    global currentPlaceIndex
    if currentPlaceIndex < len(orderOfPlaces) -1:
        currentPlaceIndex += 1
    return orderOfPlaces[currentPlaceIndex]

def prevPlace() -> PLACE:
    global currentPlaceIndex
    if currentPlaceIndex > 0:
        currentPlaceIndex -= 1
    return orderOfPlaces[currentPlaceIndex]

def currentPlace() -> PLACE:
    global currentPlaceIndex
    return orderOfPlaces[currentPlaceIndex]


BRIGHTNESS_MAX = 1
BRIGHTNESS_MIN = 0.2

class Monitor:
    brightness = 0.6
    gamma = [1.0,1.0,1.0]
    place: PLACE
    strAdapter: str

    def __init__(self, place: PLACE):
        """Set the location on the table when creating a monitor"""
        self.place = place
        self.strAdapter = adapters[place]
    
    def xrandrString(self):
        strGamma = ''
        for item in self.gamma:
            if strGamma != '' :
                strGamma += ":"
            strGamma += str(item)
        # TODO add gamma to return string
        return 'xrandr --output ' + self.strAdapter + ' --brightness ' + str(self.brightness)

    def xrandrCommand(self):
        subprocess.run(self.xrandrString(), shell=True)

    def jsonObject(self):
        gamma = json.dumps(self.gamma)
        brightness = round(self.brightness, 2)
        j = f"""{{
            "device": "monitor",
            "adapter": "{self.strAdapter}",
            "place": "{self.place.name}",
            "brightness": {brightness},
            "gamma":{gamma}
            }}"""   
        return json.loads(j)     
    def parseJson(jsonObject):
        for place in PLACE:
            if place.name == jsonObject['place']:
                newMonitor = Monitor(place)
                newMonitor.strAdapter = jsonObject['adapter']
                newMonitor.brightness =  jsonObject['brightness']
                newMonitor.gamma = jsonObject['gamma']
                return place, newMonitor

monitors: 'dict[PLACE, Monitor]' = {}

def saveSettings():
    monitorsArray = []
    for m in monitors.values():
        monitorsArray.append(m.jsonObject())
    with open("monitors.json", "w") as write_file:
        json.dump(monitorsArray, write_file, indent=4)

def loadSettings():
    try:
        with open("monitors.json", "r") as read_file:
            monitorsArray = json.load(read_file)
        for monitorJson in monitorsArray:
            place, newMonitor = Monitor.parseJson(monitorJson)
            monitors[place] = newMonitor
        # print("monitors.json was read correctly")
        return monitorsArray
    except FileNotFoundError:
        # print("monitors.json not found")
        for p in adapters.keys():
            m=Monitor(p)
            monitors[p] = m

def getMonitor(place: PLACE) -> Monitor:
    for m in monitors.values():
        if m.place is place:
            return m

def brightnessPlus():
    if currentPlace() is PLACE.ALL:
        for m in monitors.values():
            if (m.brightness * 1.1) < BRIGHTNESS_MAX:
                m.brightness *= 1.1
                m.xrandrCommand()
    else:
        m = getMonitor(currentPlace())
        if (m.brightness * 1.1) < BRIGHTNESS_MAX:
            m.brightness *= 1.1
            m.xrandrCommand()

def brightnessMinus():
    if currentPlace() is PLACE.ALL:
        for m in monitors.values():
            if (m.brightness / 1.1) > BRIGHTNESS_MIN:
                m.brightness /= 1.1
                m.xrandrCommand()
    else:
        m = getMonitor(currentPlace())
        if (m.brightness / 1.1) > BRIGHTNESS_MIN:
            m.brightness /= 1.1
            m.xrandrCommand()

def refreshBrightness():
    for m in monitors.values():
        m.xrandrCommand()

def main(stdscr):

    def printTable():
        headers = [" ", "Monitor", "Brightness"]
        width = [5,12,12]
        cursor = '>>>'
        cursorAll = '>'
        i = 0
        headerString = ''
        for header in headers:
            headerString += f'{header:<{width[i]}}'
            i += 1
        stdscr.move(0, 0)
        stdscr.addstr(headerString)
        rowNumber = 1
        for place in orderOfPlaces:
            if place != PLACE.ALL:
                row = ''
                i = 0
                if currentPlace() is place:
                    row += f'{cursor:<{width[i]}}'
                elif currentPlace() is PLACE.ALL:
                    row += f'{cursorAll:<{width[i]}}'
                else:
                    row += ' ' * width[i]
                i += 1
                m = getMonitor(place)
                row += f'{m.place.name:<{width[i]}}'
                i += 1
                brightness = f'{m.brightness:4.2f}'
                row += f'{brightness:<{width[i]}}'
                stdscr.move(rowNumber, 0)
                stdscr.addstr(row)
                rowNumber +=1

    printTable()

    stdscr.nodelay(1)   
    stdscr.timeout(100) 

    while True:
        # get keyboard input, returns -1 if none available
        c = stdscr.getch()
        if c != -1:
            if c == 259: #Up
                prevPlace()
            if c == 258: #Down
                nextPlace()
            if c == 261: #Left
                brightnessPlus()
            if c == 260: #Right
                brightnessMinus()
            if c in {258,259,260,261}:
                printTable()
            if c == 32: #space
                refreshBrightness()
            if c == 113: # press "q" for exit
                saveSettings()
                sys.exit()

print('\33]0;Xrandr-Brightness\a', end='', flush=True)
loadSettings()
setOrder()
atexit.register(saveSettings)
signal.signal(signal.SIGHUP, saveSettings)
signal.signal(signal.SIGINT, saveSettings)
refreshBrightness()
curses.wrapper(main)