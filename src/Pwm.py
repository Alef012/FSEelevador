import RPi.GPIO as GPIOControl
from time import sleep
import logging
import os
from UART import solicita_valor_encoder, enviar_sinal_pwm
from PID import PIDController

# Suppress RPi.GPIO warnings
GPIOControl.setwarnings(False)
logging.getLogger("RPi.GPIO").setLevel(logging.ERROR)

# GPIO Pins Setup
MOTOR_UP_PIN = 20
MOTOR_DOWN_PIN = 21
MOTOR_SPEED_PIN = 12
BASE_FLOOR_PIN = 18
FIRST_LEVEL_PIN = 23
SECOND_LEVEL_PIN = 24
TOP_FLOOR_PIN = 25

# RPi.GPIO Library Configuration
GPIOControl.setmode(GPIOControl.BCM)
GPIOControl.setup(MOTOR_UP_PIN, GPIOControl.OUT)
GPIOControl.setup(MOTOR_DOWN_PIN, GPIOControl.OUT)
GPIOControl.setup(MOTOR_SPEED_PIN, GPIOControl.OUT)

GPIOControl.setup(BASE_FLOOR_PIN, GPIOControl.IN)
GPIOControl.setup(FIRST_LEVEL_PIN, GPIOControl.IN)
GPIOControl.setup(SECOND_LEVEL_PIN, GPIOControl.IN)
GPIOControl.setup(TOP_FLOOR_PIN, GPIOControl.IN)

elevador_pwm = GPIOControl.PWM(MOTOR_SPEED_PIN, 1000)



def inicia_pwm():
    elevador_pwm.start(0)


def para_pwm():
    elevador_pwm.stop()


def ajusta_velocidade_motor(power_level):
    elevador_pwm.ChangeDutyCycle(power_level)


def opera_motor(direction, power_level=100):
    if direction == (1, 0):
        GPIOControl.output(MOTOR_UP_PIN, 1)
        GPIOControl.output(MOTOR_DOWN_PIN, 0)
        ajusta_velocidade_motor(power_level)
    elif direction == (0, 1):
        GPIOControl.output(MOTOR_UP_PIN, 0)
        GPIOControl.output(MOTOR_DOWN_PIN, 1)
        ajusta_velocidade_motor(power_level)
    elif direction == (1, 1):
        GPIOControl.output(MOTOR_UP_PIN, 1)
        GPIOControl.output(MOTOR_DOWN_PIN, 1)
        ajusta_velocidade_motor(power_level)
    else:
        GPIOControl.output(MOTOR_UP_PIN, 0)
        GPIOControl.output(MOTOR_DOWN_PIN, 0)
        ajusta_velocidade_motor(0)

def verifica_sensores():
    return {
        "Ground_Sensor": GPIOControl.input(BASE_FLOOR_PIN),
        "First_Floor_Sensor": GPIOControl.input(FIRST_LEVEL_PIN),
        "Second_Floor_Sensor": GPIOControl.input(SECOND_LEVEL_PIN),
        "Third_Floor_Sensor": GPIOControl.input(TOP_FLOOR_PIN),
    }

def encontra_andares(uart_stream):
    print("Começando Procura dos andares")
    terreo = None
    primeiro_andar = None
    segundo_andar= None
    terceiro_andar= None
    while True:

        inicia_pwm()
        opera_motor((1, 0), 1)
    
        sensor_states = verifica_sensores()
        if sensor_states["Ground_Sensor"]:
            terreo = solicita_valor_encoder(uart_stream)
            print("Elevator at ground floor", terreo)           
        elif sensor_states["First_Floor_Sensor"]:
            primeiro_andar = solicita_valor_encoder(uart_stream)
            print("Elevator at first floor", primeiro_andar)
        elif sensor_states["Second_Floor_Sensor"]:
            segundo_andar = solicita_valor_encoder(uart_stream)
            print("Elevator at second floor", segundo_andar)
        elif sensor_states["Third_Floor_Sensor"]:
            terceiro_andar = solicita_valor_encoder(uart_stream)
            print("Elevator at third floor", terceiro_andar)
        if terreo and primeiro_andar and segundo_andar and terceiro_andar:
                para_pwm()
                logging.info("All floors recognized")
                return terreo,primeiro_andar,segundo_andar,terceiro_andar
        sleep(0.05)

def va_para_andar(andar_alvo,uarto_filestream,nome_andar):
    pid = PIDController() 
    pid.atualiza_referencia(andar_alvo)
    andar_atual= solicita_valor_encoder(uarto_filestream)
    inicia_pwm()
    
    while True:      
        andar_atual=solicita_valor_encoder(uarto_filestream)
        controle = pid.controle(andar_atual)
        enviar_sinal_pwm(uarto_filestream, controle)
        print(andar_alvo)
        if andar_atual > andar_alvo + 80:
            print('primeiro if')
            logging.info("Indo para andar "+ nome_andar)
            opera_motor((0,1),controle)
            sleep(0.05)
            
        elif andar_atual < andar_alvo-80:
            print('segundo if')
            logging.info("Indo para andar "+ nome_andar)
            opera_motor((1,0),controle)
            sleep(0.05)
        
        elif andar_alvo-80 <= andar_atual and andar_atual <= andar_alvo + 80:
            print('terceiro if')
            opera_motor((1,1))
            logging.info("Você chegou ao andar "+nome_andar)
            sleep(4)
            para_pwm()
            break


# uarto_filestream = os.open(
#         "/dev/serial0", os.O_RDWR | os.O_NOCTTY | os.O_NDELAY
#     )

# terreo,primeiro_andar, segundo_andar, terceiro_andar= encontra_andares(uarto_filestream)
# va_para_andar(segundo_andar, uarto_filestream, '2')





            


