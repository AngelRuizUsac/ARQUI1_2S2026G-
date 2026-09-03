import subprocess

from configuracion import (RUTA_ARM64,BINARIO_ARM64,LECTURAS_ARM64)


# Se guardan temporalmente las temperaturas 
temperaturas = []


def agregar_temperatura(temperatura):
   
    # Guarda hasta completar la cantidad que requiere para arm

    temperaturas.append(int(round(temperatura)))

    if len(temperaturas) < LECTURAS_ARM64:
        return None

    # Tomamos el grupo de lecturas
    lecturas = temperaturas[:LECTURAS_ARM64]

    # Las eliminamos de la lista
    del temperaturas[:LECTURAS_ARM64]

    return procesar_con_arm64(lecturas)


def generar_datos_txt(lecturas):
    
    # Genera el archivo datos.txt con el formato solicitado por el programa ARM64

    ruta = RUTA_ARM64 / "datos.txt"

    with open(ruta,"w",encoding="utf-8") as archivo:

        for lectura in lecturas:
            archivo.write(f"{lectura}\n")

        archivo.write("$\n")

    return ruta


def procesar_con_arm64(lecturas):

    generar_datos_txt(lecturas)

    binario = (RUTA_ARM64 / BINARIO_ARM64)

    if not binario.exists():

        print("\nTodavía no existe el ejecutable ARM64.")
        print("datos.txt fue generado correctamente.")

        return None

    try:

        subprocess.run([str(binario)],cwd=RUTA_ARM64,check=True)

        return leer_resultado()

    except Exception as error:

        print(f"Error ejecutando ARM64: {error}")

        return None


def leer_resultado():
    # Lee resultado.txt generado por el programa ARM64

    ruta = (RUTA_ARM64 / "resultado.txt")

    if not ruta.exists():
        return None

    resultado = {}

    with open(ruta,"r", encoding="utf-8") as archivo:

        lineas = archivo.readlines()

    for linea in lineas:

        linea = linea.strip()

        # Formato final requerido
        # MAX=27
        # MIN=21
        # AVG=24
        # COUNT=20

        if linea.startswith("MAX="):
            resultado["maximo"] = int(linea.split("=")[1])

        elif linea.startswith("MIN="):
            resultado["minimo"] = int(linea.split("=")[1])

        elif linea.startswith("AVG="):
            resultado["promedio"] = int(linea.split("=")[1])

        elif linea.startswith("COUNT="):
            resultado["cantidad"] = int(linea.split("=")[1])

        # Compatibilidad temporal con el ensamblador 
        elif linea.startswith("Maximo:"):
            resultado["maximo"] = int(linea.split(":")[1])

        elif linea.startswith("Minimo:"):
            resultado["minimo"] = int(linea.split(":")[1])

        elif linea.startswith("Promedio:"):
            resultado["promedio"] = int(linea.split(":")[1])

        elif linea.startswith("Cantidad:"):
            resultado["cantidad"] = int(linea.split(":")[1])

    return resultado