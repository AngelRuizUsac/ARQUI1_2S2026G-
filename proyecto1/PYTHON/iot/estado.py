from configuracion import (TEMPERATURA_MAXIMA,HUMEDAD_MINIMA,HUMEDAD_MAXIMA,GAS_MAXIMO)


def obtener_estado(datos):
    
    # Determina el estado general del edificio


    temperatura = datos["temperatura"]
    humedad = datos["humedad"]
    gas = datos["gas"]

    # El gas tiene mayor prioridad
    if gas > GAS_MAXIMO:
        return "EMERGENCIA"

    # Temperatura o humedad fuera de rango
    if (temperatura > TEMPERATURA_MAXIMA or humedad < HUMEDAD_MINIMA or humedad > HUMEDAD_MAXIMA):
        return "ADVERTENCIA"

    return "NORMAL"