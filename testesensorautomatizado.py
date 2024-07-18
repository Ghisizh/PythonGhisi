import sys
from canlib import canlib, Frame




def printframe(frame, width):
    form = '═^' + str(width - 1)
    print(format(" Frame received ", form))
    print("id:", hex(frame.id))
    print("dlc:", frame.dlc)
    print("data:", bytes(frame.data))
    print("timestamp:", frame.timestamp)


def calculadados(byte1, byte2, slope, offset, decimal):
    result = (((byte2 * 256) + byte1) * slope) - offset
    return round(result, decimal)


def mensagefilter(code, mask):
    msg_filter = canlib.objbuf.MessageFilter(code=code, mask=mask)
    return msg_filter


def createframe(id, data):
    frame = Frame(id_=id, dlc=8, data=data, flags=canlib.canMSG_EXT)
    return frame


def main(channel_index):
    ch = canlib.openChannel(channel=int(channel_index))
    ch.setBusParams(canlib.canBITRATE_250K)
    ch.busOn()
    msgdewon = createframe(0x18fedf00, [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf7])
    msgdewoff = createframe(0x18fedf00, [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf3])
    msgdatafilternorma = mensagefilter(0x00f00f00, 0x00ffff00)
    contador = 0
    amostras = 0

    aquecendo_displayed = False  # Variável para controlar a exibição da mensagem "Aquecendo"

    print("Listening...")
    while True:
        try:
            frame = ch.read(timeout=500)
            if msgdatafilternorma(frame.id):
                if contador == 0:
                    ch.write(msgdewon)
                    print("Dew point ON")
                    contador += 1

                if contador == 1:
                    if frame.data[5] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[5] == 0xbf:
                        if not aquecendo_displayed:  # Verifica se a mensagem já foi exibida
                            print("Aquecendo")
                            aquecendo_displayed = True  # Atualiza a variável para evitar exibições futuras
                    elif frame.data[5] == 0x9f:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1

                if contador > 1:
                    try:
                        if msgdatafilternorma(frame.id):
                            nox_value = calculadados(frame.data[0], frame.data[1], 0.05, 200, 0)
                            o2_value = calculadados(frame.data[2], frame.data[3], 0.000514, 12, 1)
                            # Limpa a linha atual e escreve os novos valores
                            sys.stdout.write(f"\rNox= {nox_value} ppm, O2= {o2_value} %")
                            sys.stdout.flush()
                            if nox_value < 5:
                                amostras += 1
                            if amostras > 150:
                                print("\n===============================================")
                                print("\nValor estável")
                                print(f"Nox= {nox_value} ppm, O2= {o2_value} %")
                                ch.write(msgdewoff)
                                break


                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")
                        # Continua o loop para tentar novamente

        except canlib.CanNoMsg:
            print("Can no msg")
        except KeyboardInterrupt:
            print("Stop.")
            break

    ch.busOff()
    ch.close()


if __name__ == "__main__":
    main(0)
