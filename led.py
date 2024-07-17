from canlib import canlib
ch = canlib.openChannel(channel=0)
ch.flashLeds(canlib.kvLED_ACTION_ALL_LEDS_ON, 10000)