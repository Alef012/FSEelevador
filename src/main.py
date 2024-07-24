import signal
import sys
import logging
import os
import termios
from time import sleep
from Pwm import encontra_andares, va_para_andar
from threading import Thread, Event, Lock
from i2c import atualiza_temperatura
import time

exit_execution = Event()
uart_lock = Lock()

terreo = None
primeiro_andar = None
segundo_andar= None
terceiro_andar= None

if __name__ == "__main__":
    
    def menu():
        while True:
            if exit_execution.is_set():
                break
            else:
                sleep(8)
                os.system('clear')
                print('*'*31)
                print("*  Para Qual Andar Deseja Ir  *")
                print("*  (T, 1, 2, 3)  *")
                print('*'*31)

    def escolha_andar():
        while True:
            if exit_execution.is_set():
                break
            else:
                andar = input('')
                with uart_lock:
                    if andar == 't' or andar == 'T':
                        va_para_andar(terreo,uarto_filestream,'terreo')
                    elif andar == '1':
                        va_para_andar(primeiro_andar,uarto_filestream,'1')
                    elif andar == '2':
                        va_para_andar(segundo_andar,uarto_filestream,'2')
                    elif andar == '3':
                        va_para_andar(terceiro_andar, uarto_filestream, '3')

    def repetir_atualiza_temperatura(uarto_filestream):
        while not exit_execution.is_set():
            with uart_lock:
                atualiza_temperatura(uarto_filestream)
            time.sleep(1)
       
    def the_end(sig, frama):
            exit_execution.set()
            print("the end ...")
            sleep(2)
            sys.exit(0)

    uarto_filestream = None
    try:
        uarto_filestream = os.open(
            "/dev/serial0", os.O_RDWR | os.O_NOCTTY | os.O_NDELAY
        )

        [iflag, oflag, cflag, lflag] = [0, 1, 2, 3]

        attrs = termios.tcgetattr(uarto_filestream)

        attrs[cflag] = termios.B115200 | termios.CS8 | termios.CLOCAL | termios.CREAD
        attrs[iflag] = termios.IGNPAR
        attrs[oflag] = 0
        attrs[lflag] = 0

        termios.tcflush(uarto_filestream, termios.TCIFLUSH)
        termios.tcsetattr(uarto_filestream, termios.TCSANOW, attrs)

        terreo, primeiro_andar, segundo_andar, terceiro_andar = encontra_andares(uarto_filestream)
        temp= Thread(target=repetir_atualiza_temperatura,args=(uarto_filestream,))
        
       
        

        menuzim = Thread(target=menu)
        escolha = Thread(target=escolha_andar)
        
        menuzim.daemon = True
        temp.daemon = True
        escolha.daemon = True
        signal.signal(signal.SIGINT, the_end)
        signal.signal(signal.SIGTERM, the_end)
        menuzim.start()
        escolha.start()
        temp.start()
        temp.join()  
        menuzim.join()
        escolha.join()
        
    except OSError as e:
        logging.error(f"Erro ao abrir a porta serial: {e}")
    finally:
        if uarto_filestream:
            os.close(uarto_filestream)
    

