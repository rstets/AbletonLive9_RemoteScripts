# Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/SpeedLink/__init__.py
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.TransportComponent import TransportComponent
CHANNEL = 5
PLAY_BUTTON = 40
STOP_BUTTON = 42
RECORD_BUTTON = 41
TAP_TEMPO_BUTTON = 43

class SpeedLink(ControlSurface):

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        transport = TransportComponent()


def create_instance(c_instance):
    """ The generic script can be customised by using parameters (see config.py). """
    return SpeedLink(c_instance)