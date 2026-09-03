import os
from pathlib import Path
from dotenv import load_dotenv


# Carga las variables guardadas en el archivo .env
load_dotenv()


def obtener_booleano(nombre, valor_por_defecto="false"):

    # Convierte una variable del archivo .env en True o False

    valor = os.getenv(nombre, valor_por_defecto)
    return valor.lower() == "true"


# Configuración general del sistema

MODO_SIMULACION = obtener_booleano("MODO_SIMULACION", "true")

INTERVALO_LECTURA = int(os.getenv("INTERVALO_LECTURA", "5"))


## Configuración de los sensores y actuadores

TEMPERATURA_MAXIMA = float(os.getenv("TEMPERATURA_MAXIMA", "30"))

HUMEDAD_MINIMA = float(os.getenv("HUMEDAD_MINIMA", "40"))

HUMEDAD_MAXIMA = float(os.getenv("HUMEDAD_MAXIMA", "70"))

GAS_MAXIMO = int(os.getenv("GAS_MAXIMO", "700"))

LUZ_MINIMA = int(os.getenv("LUZ_MINIMA", "40"))

DISTANCIA_PUERTA = float(os.getenv("DISTANCIA_PUERTA", "20")) 


# MQTT Confi !!!!!!! 

MQTT_ACTIVO = obtener_booleano("MQTT_ACTIVO", "false")  

MQTT_BROKER = os.getenv("MQTT_BROKER","localhost")

MQTT_PUERTO = int(os.getenv("MQTT_PUERTO", "1883"))

MQTT_USUARIO = os.getenv("MQTT_USUARIO","")

MQTT_PASSWORD = os.getenv("MQTT_PASSWORD","")

MQTT_TLS = obtener_booleano("MQTT_TLS","false")

IDENTIFICADOR_UNICO = os.getenv("IDENTIFICADOR_UNICO","ARQUI1")


# MONGO Confi

MONGO_ACTIVO = obtener_booleano("MONGO_ACTIVO","false")

MONGO_URI = os.getenv("MONGO_URI","")

MONGO_BASE_DATOS = os.getenv("MONGO_BASE_DATOS","edificio_inteligente")


# arm64 Confi

# Cantidad de temperaturas que se enviarán al módulo ARM64.
LECTURAS_ARM64 = int(os.getenv("LECTURAS_ARM64", "20"))

# proyecto1/
RUTA_PROYECTO = Path(__file__).resolve().parent.parent

# proyecto1/ARM64/
RUTA_ARM64 = RUTA_PROYECTO / "ARM64"

BINARIO_ARM64 = os.getenv("BINARIO_ARM64","programa")