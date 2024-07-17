from canlib import canlib, Frame
import time

def main():
    # Abrir o canal CAN
    ch_a = canlib.openChannel(channel=0,flags=canlib.canOPEN_ACCEPT_VIRTUAL)

    try:
        # Configurar os parâmetros do barramento CAN para 250 kbps
        ch_a.setBusParams(canlib.canBITRATE_250K)

        # Ativar o barramento CAN
        ch_a.busOn()
        print("Barramento CAN ativado. Aguardando mensagens...")

        # Loop contínuo para ler mensagens
        while True:
            try:
                # Ler a próxima mensagem disponível, com um tempo limite de 500 ms
                msg = ch_a.read(timeout=50000)
                print(f"Mensagem recebida: ID={hex(msg.id)}, Dados={msg.data}, Flags={msg.flags}")

            except canlib.canNoMsg:
                print("Nenhuma mensagem recebida dentro do tempo limite.")

            except canlib.canError as e:
                print(f"Erro ao ler a mensagem: {e}")

            # Aguarde um curto período antes de tentar ler novamente
            time.sleep(0.1)

    except Exception as e:
        print(f"Erro na configuração do canal CAN: {e}")

    finally:
        # Desativar o barramento CAN e fechar o canal
        ch_a.busOff()
        ch_a.close()
        print("Barramento CAN desativado e canal fechado.")

if __name__ == "__main__":
    main()
