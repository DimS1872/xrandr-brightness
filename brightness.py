import sys
import subprocess 
import enum
import curses
import json

class PLACE (enum.IntEnum):
    Left = 1
    Middle = 2
    Right = 3

    def prev(self):
        if self is PLACE.Left:
            return PLACE.Left
        if self is PLACE.Middle:
            return PLACE.Left
        if self is PLACE.Right:
            return PLACE.Middle
            
        
       
    def next(self):
        if self is PLACE.Left:
            return PLACE.Middle
        if self is PLACE.Middle:
            return PLACE.Right
        if self is PLACE.Right:
            return PLACE.Right
       

ADAPTERS = {PLACE.Left:'DP-1',
            PLACE.Middle: 'HDMI-1',
            PLACE.Right: 'DVI-D-1-1'}

BRIGHTNESS_MAX = 1
BRIGHTNESS_MIN = 0.2
BRIGHTNESS_STEP = 0.025


class Monitor:
    """Monitor"""
    brightness = 0.6
    gamma = [0.8,0.8,0.8]
    place: PLACE
    strAdapter: str


    def __init__(self, place: PLACE):
        """Constructor"""
        self.place = place
        self.strAdapter = ADAPTERS[place]
    
    def xrandrString(self):
        strGamma = ''
        for item in self.gamma:
            if strGamma != '' :
                strGamma += ":"
            strGamma += str(item) 
        strOtput = 'xrandr --output ' + self.strAdapter + ' --brightness ' + str(self.brightness)   
        # strOtput = 'xrandr --output ' + self.strAdapter + ' --brightness ' + str(self.brightness) +  ' --gamma ' + strGamma
        # print(strOtput)
        return strOtput
        
    def tuning(self):
        subprocess.run(self.xrandrString(), shell=True)

    def jsonObject(self):
        gamma = json.dumps(self.gamma)
        j = f"""{{
            "device": "monitor",
            "adapter": "{self.strAdapter}",
            "place": "{self.place.name}",
            "brightness": {self.brightness},
            "gamma":{gamma}
            }}"""   
        return json.loads(j)     
        # return json.dumps(j)





def main(stdscr):
    # do not wait for input when calling getch
    print('-----')

    def saveSettings(monitors):
        monitorsArray = []
        for p in PLACE:            
           monitorsArray.append(monitors[p].jsonObject())
        with open("monitors.json", "w") as write_file:            
            json.dump(monitorsArray, write_file, indent=4)           



    def message(m:Monitor):
        s = (str(m.place.name) + ' monitor: Brightness = ' + f'{m.brightness:4.3f}' + '        ') 
        stdscr.addstr(s) 
        stdscr.refresh()            
        stdscr.move(0, 0) 

  

    currentPlace = PLACE.Left
    monitors: dict[PLACE, Monitor] = {}
    for p in PLACE:
        m=Monitor(p)
        monitors[p] = m

    message(monitors[currentPlace])
     
    stdscr.nodelay(1)   
    stdscr.timeout(100) 

    while True:
        # get keyboard input, returns -1 if none available
        c = stdscr.getch()
        if c != -1:
            if c == 260:
                currentPlace = currentPlace.prev()
            if c == 261:
                currentPlace = currentPlace.next()
            m = monitors[currentPlace]
            if c == 258:
                if m.brightness > BRIGHTNESS_MIN:
                    m.brightness -= BRIGHTNESS_STEP
                    m.tuning()
            if c == 259:
                if m.brightness < BRIGHTNESS_MAX:
                    m.brightness += BRIGHTNESS_STEP
                    m.tuning()
            if c in {258,259,260,261}:
                message(monitors[currentPlace])  
            if c == 113: # press "q" for exit
                saveSettings(monitors)
                #Ssys.exit()
  
def loadSettings():
    with open("monitors.json", "r") as read_file:
        monitorsArray = json.load(read_file)
    print("a", monitorsArray[0]['device'])   
loadSettings()
curses.wrapper(main)


