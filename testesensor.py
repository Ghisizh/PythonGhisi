import sys
from canlib import canlib, Frame

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

    contador = 0
    amostras = 0
    #J1939
    msgdewonnorma = createframe(0x18fedf00, [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf7])
    msgdewoffnorma = createframe(0x18fedf00, [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf3])
    msgdatafilternorma = mensagefilter(0x00f00f00, 0x00ffff00)
    #MBB
    msgdewonmbb = createframe(0x18ff2000, [0xb0, 0xc4, 0xf7, 0xff, 0xff, 0xff, 0xfd, 0xf7])
    msgdewoffmbb = createframe(0x18ff2000, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msgdatafiltermbb = mensagefilter(0x00ff2d52,0x00ffff00)
    #VOLVO
    msgdewonvolvo = createframe(0x0cff1400, [0x80, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
    msgdewoffvolvo = createframe(0x0cff1400, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msgdatafiltervolvo = mensagefilter(0x00ff1700,0x00ffff00)
    #IVECO
    msgdewoniveco = createframe(0x1807043d, [0x80, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
    msgdewoffiveco = createframe(0x1807043d, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msgdatafilteriveco = mensagefilter(0x0007033d,0x00ffff00)
    #SCANIA
    msgdewoonscania = createframe(0x18ffb100, [0x80, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
    msgdewoffscania = createframe(0x18ffb100, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msgdatafilterscania = mensagefilter(0x00ffc200,0x00ffff00)


    aquecendo_displayed = False  # Variável para controlar a exibição da mensagem "Aquecendo"
    sensorid_displayed = False
    print("Listening...")
    while True:
        try:
            frame = ch.read(timeout=500)

            ##SENSOR NORMA
            if msgdatafilternorma(frame.id):
                if not sensorid_displayed:
                    print("Sensor dentro da norma J1939")
                    sensorid_displayed = True
                if contador == 0:
                    ch.write(msgdewonnorma)
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
                                ch.write(msgdewoffnorma)
                                break


                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")
                        # Continua o loop para tentar novamente
            ##SENSOR MBB
            if msgdatafiltermbb(frame.id):
                if not sensorid_displayed:
                    print("Sensor fabricante MBB")
                    sensorid_displayed = True
                if contador == 0:
                    ch.write(msgdewonmbb)
                    print("Dew point ON")
                    contador += 1

                if contador == 1:
                    if frame.data[6] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[6] == 0x05:
                        if not aquecendo_displayed:  # Verifica se a mensagem já foi exibida
                            print("Aquecendo")
                            aquecendo_displayed = True  # Atualiza a variável para evitar exibições futuras
                    elif frame.data[6] == 0x55:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1

                if contador > 1:
                    try:
                        if msgdatafiltermbb(frame.id):
                            nox_value = calculadados(frame.data[0], frame.data[1], 1, 0, 0)
                            o2_value = calculadados(frame.data[2], frame.data[3], -0.0186, -20.9, 1)
                            # Limpa a linha atual e escreve os novos valores
                            sys.stdout.write(f"\rNox= {nox_value} ppm, O2= {o2_value} %")
                            sys.stdout.flush()
                            if nox_value < 5:
                                amostras += 1
                            if amostras > 150:
                                print("\n===============================================")
                                print("\nValor estável")
                                print(f"Nox= {nox_value} ppm, O2= {o2_value} %")
                                ch.write(msgdewoffmbb)
                                break


                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")
                        # Continua o loop para tentar novamente
            ##SENSOR VOLVO
            if msgdatafiltervolvo(frame.id):
                if not sensorid_displayed:
                    print("Sensor fabricante VOLVO")
                    sensorid_displayed = True
                if contador == 0:
                    ch.write(msgdewonvolvo)
                    print("Dew point ON")
                    contador += 1

                if contador == 1:
                    if frame.data[6] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[6] == 0x05:
                        if not aquecendo_displayed:  # Verifica se a mensagem já foi exibida
                            print("Aquecendo")
                            aquecendo_displayed = True  # Atualiza a variável para evitar exibições futuras
                    elif frame.data[6] == 0x55:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1

                if contador > 1:
                    try:
                        if msgdatafiltervolvo(frame.id):
                            nox_value = calculadados(frame.data[0], frame.data[1], 1, 0, 0)
                            o2_value = calculadados(frame.data[2], frame.data[3], -0.0186, -21.9, 1)
                            # Limpa a linha atual e escreve os novos valores
                            sys.stdout.write(f"\rNox= {nox_value} ppm, O2= {o2_value} %")
                            sys.stdout.flush()
                            if nox_value < 5:
                                amostras += 1
                            if amostras > 150:
                                print("\n===============================================")
                                print("\nValor estável")
                                print(f"Nox= {nox_value} ppm, O2= {o2_value} %")
                                ch.write(msgdewoffvolvo)
                                break


                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")
                        # Continua o loop para tentar novamente
                ##SENSOR IVECO
            if msgdatafilteriveco(frame.id):
                if not sensorid_displayed:
                    print("Sensor fabricante IVECO")
                    sensorid_displayed = True
                if contador == 0:
                    ch.write(msgdewoniveco)
                    print("Dew point ON")
                    contador += 1

                if contador == 1:
                    if frame.data[6] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[6] == 0x05:
                        if not aquecendo_displayed:  # Verifica se a mensagem já foi exibida
                            print("Aquecendo")
                            aquecendo_displayed = True  # Atualiza a variável para evitar exibições futuras
                    elif frame.data[6] == 0x55:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1

                if contador > 1:
                    try:
                        if msgdatafilteriveco(frame.id):
                            nox_value = calculadados(frame.data[0], frame.data[1], 1, 0, 0)
                            o2_value = calculadados(frame.data[2], frame.data[3], -0.019, -21, 1)
                            # Limpa a linha atual e escreve os novos valores
                            sys.stdout.write(f"\rNox= {nox_value} ppm, O2= {o2_value} %")
                            sys.stdout.flush()
                            if nox_value < 5:
                                amostras += 1
                            if amostras > 150:
                                print("\n===============================================")
                                print("\nValor estável")
                                print(f"Nox= {nox_value} ppm, O2= {o2_value} %")
                                ch.write(msgdewoffiveco)
                                break


                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")
                        # Continua o loop para tentar novamente
                ##SENSOR SCANIA
            if msgdatafilterscania(frame.id):
                if not sensorid_displayed:
                    print("Sensor fabricante SCANIA")
                    sensorid_displayed = True
                if contador == 0:
                    ch.write(msgdewoonscania)
                    print("Dew point ON")
                    contador += 1

                if contador == 1:
                    if frame.data[6] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[6] == 0x05:
                        if not aquecendo_displayed:  # Verifica se a mensagem já foi exibida
                            print("Aquecendo")
                            aquecendo_displayed = True  # Atualiza a variável para evitar exibições futuras
                    elif frame.data[6] == 0x55:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1

                if contador > 1:
                    try:
                        if msgdatafilterscania(frame.id):
                            nox_value = calculadados(frame.data[0], frame.data[1], 1, 26, 0)
                            o2_value = calculadados(frame.data[2], frame.data[3], -0.0186, -20.6, 1)
                            # Limpa a linha atual e escreve os novos valores
                            sys.stdout.write(f"\rNox= {nox_value} ppm, O2= {o2_value} %")
                            sys.stdout.flush()
                            if nox_value < 5:
                                amostras += 1
                            if amostras > 150:
                                print("\n===============================================")
                                print("\nValor estável")
                                print(f"Nox= {nox_value} ppm, O2= {o2_value} %")
                                ch.write(msgdewoffscania)
                                break


                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")
                        # Continua o loop para tentar novamente

        except canlib.CanNoMsg:
            sys.stdout.write(f"\rNo CAN Msg")
            sys.stdout.flush()
        except KeyboardInterrupt:
            print("Stop.")
            break

    ch.busOff()
    ch.close()


if __name__ == "__main__":
    main(0)
