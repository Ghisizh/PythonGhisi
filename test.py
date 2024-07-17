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


def mensagefilter(code, mask):
    msg_filter = canlib.objbuf.MessageFilter(code=code, mask=mask)
    return msg_filter


def createframe(id, data):
    frame = Frame(id_=id, data=data, flags=canlib.canMSG_EXT)


def main(channel_index, ticktime):
    ch = canlib.openChannel(channel=int(channel_index), flags=canlib.canOPEN_ACCEPT_VIRTUAL)
    ch.busOn()
    width, height = shutil.get_terminal_size((80, 20))

    msgdew = mensagefilter(0x00fedf00, 0x00FFFF00)
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

            if msgdew(frame.id):
                printframe(frame, width)
                print(hex(frame.data[7]))
                if frame.data[7] == 0xf7:
                    print("Dew point ON")
                elif frame.data[7] == 0xf3:
                    print("Dew point OFF")
            else:

                print("mensagem nao aceita")
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
