import termios
import os
import struct
import logging
from time import sleep
from crc import calcula_CRC
import threading

ADDRESS = 0x01
REQUEST = 0x23
SEND = 0x16

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

MATRICULA = '2532'

def validacao(codes, crc):

    res_crc = calcula_CRC(codes)
    if res_crc == crc:
        return True
    else:
        logging.warning("Erro de comunicação")
        return False


def solicita_valor_encoder(uarto_filestream):
    while True:
        termios.tcflush(uarto_filestream, termios.TCIFLUSH)
        buffer = bytearray()

        buffer.append(ADDRESS)
        buffer.append(REQUEST)
        buffer.append(0xC1)
        for digito in MATRICULA:
            buffer.append(int(digito))
        crc = calcula_CRC(buffer)
        buffer.extend(crc)

        os.write(uarto_filestream, bytes(buffer))

        sleep(0.2)  

        resposta = os.read(uarto_filestream, 255)  

        crc_recebido = resposta[-2:]

        if validacao(resposta[:-2], crc_recebido):
            valor_encoder = int.from_bytes(resposta[3:7], byteorder='little', signed=True) 
            logging.info(f"Encoder value: {valor_encoder}")
            return valor_encoder
        break


def enviar_sinal_pwm(uarto_filestream, valor_pwm):
    while True:
        termios.tcflush(uarto_filestream, termios.TCIFLUSH)
        buffer = bytearray()
        buffer.append(ADDRESS)
        buffer.append(SEND)
        buffer.append(0xC2)
        buffer.extend(struct.pack("<i", valor_pwm))
        for digito in MATRICULA:
            buffer.append(int(digito))  
        crc = calcula_CRC(buffer)
        buffer.extend(crc)

        os.write(uarto_filestream, bytes(buffer))

        sleep(0.2)
        resposta = os.read(uarto_filestream, 255)  

        crc_recebido = resposta[-2:]


        if validacao(resposta[:-2], crc_recebido):
            return resposta


def enviar_temperatura_ambiente(uarto_filestream, temperatura):
    while True:
        termios.tcflush(uarto_filestream, termios.TCIFLUSH)
        buffer = bytearray()
        buffer.append(ADDRESS)
        buffer.append(SEND)
        buffer.append(0xD1)
        buffer.extend(struct.pack("<f", temperatura))
        for digito in MATRICULA:
            buffer.append(int(digito))
        crc = calcula_CRC(buffer)
        buffer.extend(crc)

        os.write(uarto_filestream, bytes(buffer))
        
        sleep(0.2)
        resposta = os.read(uarto_filestream, 255) 

        crc_recebido = resposta[-2:]

        if validacao(resposta[:-2], crc_recebido):
            break



def ler_registradores_botoes(uarto_filestream, endereco_inicial, quantidade_bytes):
    while True:
        termios.tcflush(uarto_filestream, termios.TCIFLUSH)
        buffer = bytearray()
        buffer.append(ADDRESS)
        buffer.append(0x03)  
        buffer.append(endereco_inicial)  
        buffer.append(quantidade_bytes) 
        for digito in MATRICULA:
            buffer.append(int(digito))  
        crc = calcula_CRC(buffer)
        buffer.extend(crc)

        os.write(uarto_filestream, bytes(buffer))

        sleep(0.2)  

        resposta = os.read(uarto_filestream, 255)  
        crc_recebido = resposta[-2:]
        if (validacao(resposta[:-2],crc_recebido)):
            dados = []
            dados_lidos = resposta[2:2 + quantidade_bytes]
            for i in dados_lidos:
                dados.append(i)
            return dados
        else:
            logging.error("Resposta inválida ou erro na comunicação.")
        
def escrever_registradores_botoes(uarto_filestream, endereco_inicial,quantidade_bytes, dados):
    termios.tcflush(uarto_filestream, termios.TCIFLUSH)
    buffer = bytearray()
    buffer.append(ADDRESS)
    buffer.append(0x06) 
    buffer.append(endereco_inicial) 
    buffer.append(quantidade_bytes) 
    buffer.append(dados)  
    for digito in MATRICULA:
        buffer.append(int(digito)) 
    crc = calcula_CRC(buffer)
    buffer.extend(crc)

    os.write(uarto_filestream, bytes(buffer))

    sleep(0.2) 

    resposta = os.read(uarto_filestream, 255)

    crc_recebido = resposta[-2:]

    logging.info(f'resposta:{resposta}')

    if validacao(resposta[:-2], crc_recebido):
        logging.info("Mensagem recebida e confirmada pela ESP32.")
        return True
    else:
        logging.error("Resposta inválida ou erro na comunicação.")
        return False
        

def main():
    uarto_filestream = None
    try:
        uarto_filestream = os.open(
            "/dev/serial0", os.O_RDWR | os.O_NOCTTY | os.O_NDELAY
        )

        [iflag, oflag, cflag, lflag] = [0, 1, 2, 3]

        attrs: termios._Attr = termios.tcgetattr(uarto_filestream)

        attrs[cflag] = termios.B115200 | termios.CS8 | termios.CLOCAL | termios.CREAD
        attrs[iflag] = termios.IGNPAR
        attrs[oflag] = 0
        attrs[lflag] = 0

        termios.tcflush(uarto_filestream, termios.TCIFLUSH)
        termios.tcsetattr(uarto_filestream, termios.TCSANOW, attrs)
        
        dados= ler_registradores_botoes(uarto_filestream,0x00,11)
        escrever_registradores_botoes(uarto_filestream, 0x00,1,0)
        
        print(dados)

    except OSError as e:
        logging.error(f"Erro ao abrir a porta serial: {e}")
    finally:
        if uarto_filestream:
            os.close(uarto_filestream)


if __name__ == "__main__":
    main()