from canlib import canlib, Frame

# Defina o canal CAN a ser usado (por exemplo, o primeiro canal disponível)
channel_index = 0

def main():
    # Abrir o canal CAN
    with canlib.openChannel(channel=channel_index) as ch:
        # Ativar o barramento CAN
        ch.busOn()
        print("Barramento CAN ativado.")

        # Definir um filtro de mensagem que dispara no ID CAN 100
        msg_filter = canlib.objbuf.MessageFilter(code=100, mask=0xFFFF)

        # Crie um quadro para enviar em resposta, com ID CAN 200
        frame = Frame(id_=200, data=[1, 2, 3, 4])

        # Alocar e configurar o buffer de resposta
        response_buf = ch.allocate_response_objbuf(filter=msg_filter, frame=frame)

        # Habilitar o buffer de resposta
        response_buf.enable()
        print("Buffer de resposta configurado e habilitado. Aguardando mensagem...")

        try:
            # Loop para ler mensagens continuamente
            while True:
                # Ler a próxima mensagem disponível, com um tempo limite de 1000 ms
                frame = ch.read(timeout=1000)
                print(f"Mensagem recebida: ID={frame.id}, Dados={frame.data}, Flags={frame.flags}")

                # Verificar se a mensagem recebida corresponde ao filtro
                if frame.id == 100:
                    print("Mensagem correspondente ao filtro recebida. Resposta automática enviada.")
                    # A resposta será enviada automaticamente pelo buffer configurado

        except canlib.canNoMsg:
            print("Nenhuma mensagem recebida dentro do tempo limite.")

        except canlib.canError as e:
            print(f"Erro ao ler a mensagem: {e}")

        finally:
            # Desativar o barramento CAN
            ch.busOff()
            print("Barramento CAN desativado.")

if __name__ == "__main__":
    main()
