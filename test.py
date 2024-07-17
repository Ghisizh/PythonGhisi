import shutil

from canlib import canlib, Frame
import time

bitrates = {
    '250K': canlib.Bitrate.BITRATE_250K,
}


def printframe(frame, width):
    form = '═^' + str(width - 1)
    print(format(" Frame received ", form))
    print("id:", hex(frame.id))
    print("dlc:", frame.dlc)
    print("data:", bytes(frame.data))
    print("timestamp:", frame.timestamp)


def calculadados(byte1, byte2, slope, offset):
    return (((byte2 * 256) + byte1) * slope) - offset


def mensagefilter(code, mask):
    msg_filter = canlib.objbuf.MessageFilter(code=code, mask=mask)
    return msg_filter


def createframe(id, data):
    frame = Frame(id_=id, dlc=8, data=data, flags=canlib.canMSG_EXT)
    return frame


def main(channel_index, ticktime):
    ch = canlib.openChannel(channel=int(channel_index), flags=canlib.canOPEN_ACCEPT_VIRTUAL)
    ch.setBusParams(canlib.canBITRATE_250K)
    ch.busOn()
    width, height = shutil.get_terminal_size((80, 20))
    msgdew = createframe(0x00fedf00, [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
    msgdewfilter = mensagefilter(0x00fedf00, 0x00FFFF00)
    msgdatafilter = mensagefilter(0x00f00f00, 0x00ffff00)
    contador = 0
    timeout = 0.5
    tick_countup = 0
    if ticktime <= 0:
        ticktime = None
    elif ticktime < timeout:
        timeout = ticktime

    print("Listening...")
    while True:
        try:

            frame = ch.read(timeout=int(timeout * 1000))

            if msgdatafilter(frame.id):
                if contador == 0:
                    ch.write(msgdew)
                    if msgdewfilter(msgdew.id):
                        if frame.data[7] == 0xf7:
                            print("Dew point ON")
                        elif frame.data[7] == 0xf3:
                            print("Dew point OFF")
                    contador += 1
            if msgdewfilter(frame.id):
                if frame.data[7] == 0xf7:
                    print("Dew point ON")
                elif frame.data[7] == 0xf3:
                    print("Dew point OFF")

            if msgdatafilter(frame.id):
                if contador == 1:
                    if frame.data[5] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[5] == 0xbf:
                        print("Aquecendo")
                    elif frame.data[5] == 0x9f:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1
            if contador > 10:
                print(f"Nox= {calculadados(frame.data[0], frame.data[1], 0.05, 200)} ppm")
                print(f"02= {calculadados(frame.data[2], frame.data[3], 0.000514, 12)} %")
                break
            if contador > 1:
                if msgdatafilter(frame.id):
                    contador += 1




        except canlib.CanNoMsg:
            if ticktime is not None:
                tick_countup += timeout
                while tick_countup > ticktime:
                    print("tick")
                    tick_countup -= ticktime
        except KeyboardInterrupt:
            print("Stop.")
            break

    ch.busOff()
    ch.close()


if __name__ == "__main__":
    main(0, 0)
