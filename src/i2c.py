from bmp280 import BMP280 as SensorBMP280
import time
from UART import enviar_temperatura_ambiente
import logging
sensor = SensorBMP280()

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

def get_environment_temperature():
    temp = sensor.get_temperature()
    return temp

def formatted_temperature(temp):
    return round(temp, 2)

def atualiza_temperatura(uarto_filestream):
    try:
        current_temp = get_environment_temperature()
        formatted_temp = formatted_temperature(current_temp)
        enviar_temperatura_ambiente(uarto_filestream, formatted_temp)
        time.sleep(1)
    except Exception as e:
        print(f"Error reading temperature: {e}")

