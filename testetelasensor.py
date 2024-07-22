import tkinter as tk
from tkinter import scrolledtext
import sys
from canlib import canlib, Frame
import threading


class RedirectText(object):
    def __init__(self, widget):
        self.widget = widget

    def write(self, string):
        self.widget.config(state=tk.NORMAL)
        self.widget.insert(tk.END, string)
        self.widget.see(tk.END)
        self.widget.config(state=tk.DISABLED)

    def overwrite(self, string):
        self.widget.config(state=tk.NORMAL)
        self.widget.delete('end-2l', 'end-1l')
        self.widget.insert(tk.END, string + '\n')
        self.widget.see(tk.END)
        self.widget.config(state=tk.DISABLED)

    def flush(self):
        pass


def iniciar_script():
    global stop_threads, timer
    stop_threads = False
    botao_iniciar.config(state=tk.DISABLED, bg="grey")
    botao_reiniciar.config(state=tk.NORMAL, bg="SystemButtonFace")
    console_text.config(state=tk.NORMAL)
    console_text.delete(1.0, tk.END)
    console_text.insert(tk.END, "Script iniciado!\n")
    console_text.config(state=tk.DISABLED)
    thread = threading.Thread(target=script, args=(0,))
    thread.start()
    # Inicia o timer de 5 minutos
    timer = threading.Timer(300, timer_acabou)
    timer.start()


def reiniciar_script():
    global stop_threads, timer
    stop_threads = True
    botao_iniciar.config(state=tk.NORMAL, bg="SystemButtonFace")
    botao_reiniciar.config(state=tk.DISABLED, bg="grey")
    console_text.config(state=tk.NORMAL)
    console_text.delete(1.0, tk.END)
    console_text.insert(tk.END, "Script resetado!\n")
    console_text.config(state=tk.DISABLED)
    send_all_dewoff_messages()
    timer.cancel()


def timer_acabou():
    send_all_dewoff_messages()
    print("Tempo do programa expirado")


def send_all_dewoff_messages():
    global msgdewoffnorma, msgdewoffmbb, msgdewoffvolvo, msgdewoffiveco, msgdewoffscania,msgdewoffnormapre
    ch = canlib.openChannel(channel=0)
    ch.setBusParams(canlib.canBITRATE_250K)
    ch.busOn()
    ch.write(msgdewoffnorma)
    ch.write(msgdewoffmbb)
    ch.write(msgdewoffvolvo)
    ch.write(msgdewoffiveco)
    ch.write(msgdewoffscania)
    ch.write(msgdewoffnormapre)
    ch.busOff()
    ch.close()
    botao_iniciar.config(state=tk.NORMAL, bg="SystemButtonFace")
    botao_reiniciar.config(state=tk.DISABLED, bg="grey")


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


def script(channel_index):
    global stop_threads, msgdewoffnorma, msgdewoffmbb, msgdewoffvolvo, msgdewoffiveco, msgdewoffscania
    ch = canlib.openChannel(channel=int(channel_index))
    ch.setBusParams(canlib.canBITRATE_250K)
    ch.busOn()

    contador = 0
    amostras = 0
    msgdewonnorma = createframe(0x18fedf00, [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf7])
    msgdewoffnorma = createframe(0x18fedf00, [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xf3])
    msgdatafilternorma = mensagefilter(0x00f00f00, 0x00ffff00)
    msgdewonnormapre = createframe(0x18fedf00, [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfd])
    msgdewoffnormapre = createframe(0x18fedf00, [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfc])
    msgdatafilternormapre = mensagefilter(0x00f00e00,0x00ffff00)
    msgdewonmbb = createframe(0x0cff2029, [0xb0, 0xc4, 0xf7, 0xff, 0xff, 0xff, 0xfd, 0xff])
    msgdewoffmbb = createframe(0x0cff2029, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msgdatafiltermbb = mensagefilter(0x00ff2d52, 0x00ffff00)
    msgdewonvolvo = createframe(0x0cff1400, [0x80, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
    msgdewoffvolvo = createframe(0x0cff1400, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msgdatafiltervolvo = mensagefilter(0x00ff1700, 0x00ffff00)
    msgdewoniveco = createframe(0x1807043d, [0x80, 0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
    msgdewoffiveco = createframe(0x1807043d, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msgdatafilteriveco = mensagefilter(0x0007033d, 0x00ffff00)
    msgdewoonscania = createframe(0x18ffb100, [0x80, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff])
    msgdewoffscania = createframe(0x18ffb100, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msgdatafilterscania = mensagefilter(0x00ffc200, 0x00ffff00)

    aquecendo_displayed = False
    sensorid_displayed = False
    print("Listening...")

    while not stop_threads:
        try:
            frame = ch.read(timeout=500)
            if stop_threads:
                break

            if msgdatafilternorma(frame.id):
                if not sensorid_displayed:
                    print("Sensor dentro da norma J1939")
                    sensorid_displayed = True
                if contador == 0:
                    ch.write(msgdewonnorma)
                    ch.write(msgdewonnorma)
                    ch.write(msgdewonnorma)
                    print("Dew point ON")
                    contador += 1

                if contador == 1:
                    if frame.data[5] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[5] == 0xbf:
                        if not aquecendo_displayed:
                            print("Aquecendo")
                            aquecendo_displayed = True
                    elif frame.data[5] == 0x9f:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1

                if contador > 1:
                    try:
                        if msgdatafilternorma(frame.id):
                            nox_value = calculadados(frame.data[0], frame.data[1], 0.05, 200, 0)
                            o2_value = calculadados(frame.data[2], frame.data[3], 0.000514, 12, 1)
                            if nox_value >= 0 and o2_value >=0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                            elif nox_value < 0 and o2_value >= 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= {o2_value} %")
                            elif o2_value < 0 and nox_value >= 0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= XX %")
                            elif o2_value < 0 and nox_value < 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= XX %")

                            if nox_value < 20 and nox_value >= 0:
                                amostras += 1
                            if amostras > 500:
                                print("\n===============================================")
                                print("\nValor estável")
                                print(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                                ch.write(msgdewoffnorma)
                                ch.write(msgdewoffnorma)
                                ch.write(msgdewoffnorma)
                                break

                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")
            if msgdatafilternormapre(frame.id):
                if not sensorid_displayed:
                    print("Sensor pré catalisador dentro da norma J1939")
                    sensorid_displayed = True
                if contador == 0:
                    ch.write(msgdewonnormapre)
                    ch.write(msgdewonnormapre)
                    ch.write(msgdewonnormapre)
                    print("Dew point ON")
                    contador += 1

                if contador == 1:
                    if frame.data[5] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[5] == 0xbf:
                        if not aquecendo_displayed:
                            print("Aquecendo")
                            aquecendo_displayed = True
                    elif frame.data[5] == 0x9f:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1

                if contador > 1:
                    try:
                        if msgdatafilternormapre(frame.id):
                            nox_value = calculadados(frame.data[0], frame.data[1], 0.05, 200, 0)
                            o2_value = calculadados(frame.data[2], frame.data[3], 0.000514, 12, 1)
                            if nox_value >= 0 and o2_value >=0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                            elif nox_value < 0 and o2_value >= 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= {o2_value} %")
                            elif o2_value < 0 and nox_value >= 0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= XX %")
                            elif o2_value < 0 and nox_value < 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= XX %")

                            if nox_value < 20 and nox_value >= 0:
                                amostras += 1
                            if amostras > 500:
                                print("\n===============================================")
                                print("\nValor estável")
                                print(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                                ch.write(msgdewoffnormapre)
                                ch.write(msgdewoffnormapre)
                                ch.write(msgdewoffnormapre)
                                break

                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")
            if msgdatafiltermbb(frame.id):
                if not sensorid_displayed:
                    print("Sensor fabricante MBB")
                    sensorid_displayed = True
                if contador == 0:
                    ch.write(msgdewonmbb)
                    ch.write(msgdewonmbb)
                    ch.write(msgdewonmbb)
                    print("Dew point ON")
                    contador += 1

                if contador == 1:
                    if frame.data[6] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[6] == 0x40 or frame.data[6] == 0x41:
                        if not aquecendo_displayed:
                            print("Aquecendo")
                            aquecendo_displayed = True
                    elif frame.data[6] == 0x55:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1

                if contador > 1:
                    try:
                        if msgdatafiltermbb(frame.id):
                            nox_value = calculadados(frame.data[0], frame.data[1], 1, 0, 0)
                            o2_value = calculadados(frame.data[2], frame.data[3], -0.0186, -20.9, 1)
                            sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= {o2_value} %")

                            if nox_value >= 0 and o2_value >=0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                            elif nox_value < 0 and o2_value >= 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= {o2_value} %")
                            elif o2_value < 0 and nox_value >= 0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= XX %")
                            elif o2_value < 0 and nox_value < 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= XX %")

                            if nox_value < 20 and nox_value >= 0:
                                amostras += 1
                            if amostras > 1000:
                                print("\n===============================================")
                                print("\nValor estável")
                                print(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                                ch.write(msgdewoffmbb)
                                ch.write(msgdewoffmbb)
                                ch.write(msgdewoffmbb)
                                break

                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")

            if msgdatafiltervolvo(frame.id):
                if not sensorid_displayed:
                    print("Sensor fabricante VOLVO")
                    sensorid_displayed = True
                if contador == 0:
                    ch.write(msgdewonvolvo)
                    ch.write(msgdewonvolvo)
                    ch.write(msgdewonvolvo)
                    print("Dew point ON")
                    contador += 1

                if contador == 1:
                    if frame.data[6] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[6] == 0x40 or frame.data[6] == 0x41:
                        if not aquecendo_displayed:
                            print("Aquecendo")
                            aquecendo_displayed = True
                    elif frame.data[6] == 0x55:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1

                if contador > 1:
                    try:
                        if msgdatafiltervolvo(frame.id):
                            nox_value = calculadados(frame.data[0], frame.data[1], 1, 0, 0)
                            o2_value = calculadados(frame.data[2], frame.data[3], -0.0186, -21.9, 1)
                            if nox_value >= 0 and o2_value >=0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                            elif nox_value < 0 and o2_value >= 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= {o2_value} %")
                            elif o2_value < 0 and nox_value >= 0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= XX %")
                            elif o2_value < 0 and nox_value < 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= XX %")

                            if nox_value < 20 and nox_value >= 0:
                                amostras += 1
                            if amostras > 1000:
                                print("\n===============================================")
                                print("\nValor estável")
                                print(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                                ch.write(msgdewoffvolvo)
                                ch.write(msgdewoffvolvo)
                                ch.write(msgdewoffvolvo)
                                break

                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")

            if msgdatafilteriveco(frame.id):
                if not sensorid_displayed:
                    print("Sensor fabricante IVECO")
                    sensorid_displayed = True
                if contador == 0:
                    ch.write(msgdewoniveco)
                    ch.write(msgdewoniveco)
                    ch.write(msgdewoniveco)
                    print("Dew point ON")
                    contador += 1

                if contador == 1:
                    if frame.data[6] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[6] == 0x40 or frame.data[6] == 0x41:
                        if not aquecendo_displayed:
                            print("Aquecendo")
                            aquecendo_displayed = True
                    elif frame.data[6] == 0x55:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1

                if contador > 1:
                    try:
                        if msgdatafilteriveco(frame.id):
                            nox_value = calculadados(frame.data[0], frame.data[1], 1, 0, 0)
                            o2_value = calculadados(frame.data[2], frame.data[3], -0.019, -21, 1)
                            if nox_value >= 0 and o2_value >=0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                            elif nox_value < 0 and o2_value >= 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= {o2_value} %")
                            elif o2_value < 0 and nox_value >= 0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= XX %")
                            elif o2_value < 0 and nox_value < 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= XX %")

                            if nox_value < 20 and nox_value >= 0:
                                amostras += 1
                            if amostras > 1000:
                                print("\n===============================================")
                                print("\nValor estável")
                                print(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                                ch.write(msgdewoffiveco)
                                ch.write(msgdewoffiveco)
                                ch.write(msgdewoffiveco)
                                break

                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")

            if msgdatafilterscania(frame.id):
                if not sensorid_displayed:
                    print("Sensor fabricante SCANIA")
                    sensorid_displayed = True
                if contador == 0:
                    ch.write(msgdewoonscania)
                    ch.write(msgdewoonscania)
                    ch.write(msgdewoonscania)
                    print("Dew point ON")
                    contador += 1

                if contador == 1:
                    if frame.data[6] == 0x00:
                        print("Aquecedor aguardando")
                    elif frame.data[6] == 0x40 or frame.data[6] == 0x41:
                        if not aquecendo_displayed:
                            print("Aquecendo")
                            aquecendo_displayed = True
                    elif frame.data[6] == 0x55:
                        print("Aquecido")
                        print("Aguardando estabilizar")
                        contador += 1

                if contador > 1:
                    try:
                        if msgdatafilterscania(frame.id):
                            nox_value = calculadados(frame.data[0], frame.data[1], 1, 0, 0)
                            o2_value = calculadados(frame.data[2], frame.data[3], -0.0186, -20.6, 1)
                            if nox_value >= 0 and o2_value >=0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                            elif nox_value < 0 and o2_value >= 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= {o2_value} %")
                            elif o2_value < 0 and nox_value >= 0:
                                sys.stdout.overwrite(f"NOx= {nox_value} ppm, O2= XX %")
                            elif o2_value < 0 and nox_value < 0:
                                sys.stdout.overwrite(f"NOx= XX ppm, O2= XX %")

                            if nox_value < 20 and nox_value >= 0:
                                amostras += 1
                            if amostras > 1000:
                                print("\n===============================================")
                                print("\nValor estável")
                                print(f"NOx= {nox_value} ppm, O2= {o2_value} %")
                                ch.write(msgdewoffscania)
                                ch.write(msgdewoffscania)
                                ch.write(msgdewoffscania)
                                break

                    except Exception as e:
                        print(f"Erro ao processar a mensagem: {e}")

        except canlib.CanNoMsg:
            if stop_threads:
                break
            sys.stdout.overwrite("No CAN Msg")
        except KeyboardInterrupt:
            print("Stop.")
            break

    ch.busOff()
    ch.close()
    timer.cancel()  # Cancela o timer se o script terminar antes do tempo


root = tk.Tk()
root.title("ZHsolution")
root.geometry("800x400")
root.configure(bg="#041232")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=8)

botao_iniciar = tk.Button(root, text="Iniciar", command=iniciar_script, font=("Helvetica", 12))
botao_iniciar.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

botao_reiniciar = tk.Button(root, text="Reset", command=reiniciar_script, font=("Helvetica", 12), state=tk.DISABLED,
                            bg="grey")
botao_reiniciar.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

console_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, font=("Helvetica", 14), bg="white")
console_text.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
console_text.config(state=tk.DISABLED)

sys.stdout = RedirectText(console_text)

root.mainloop()
