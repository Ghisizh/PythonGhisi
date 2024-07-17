from canlib import canlib, Frame

ch_a = canlib.openChannel(channel=0,flags=canlib.canOPEN_ACCEPT_VIRTUAL)

id_hex = 0x00fedf00

data_hex = [0x0,0x0,0x0,0x0,0x0,0x0,0x0,0xF3]

ch_a.setBusParams(canlib.canBITRATE_250K)

ch_a.busOn()

frame =Frame(id_=id_hex, data=data_hex,dlc=8,flags=canlib.MessageFlag.EXT)
ch_a.write(frame)

ch_a.busOff()
ch_a.close()