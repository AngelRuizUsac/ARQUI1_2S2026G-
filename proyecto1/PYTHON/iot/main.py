import time

from sensores import leer_sensores
from estado import obtener_estado

from actuadores import (
    controlar_actuadores,
    ejecutar_comando
)

from configuracion import (
    INTERVALO_LECTURA
)

from base_datos import BaseDatos
from mqtt_cliente import ClienteMQTT
from arm64 import agregar_temperatura


def mostrar_informacion(
    datos,
    estado,
    actuadores
):
    """
    Muestra en consola el estado actual
    del edificio.
    """

    print("\n===================================")
    print("       EDIFICIO INTELIGENTE")
    print("===================================")

    print("\nSENSORES")

    print(
        f"Temperatura: "
        f"{datos['temperatura']} °C"
    )

    print(
        f"Humedad: "
        f"{datos['humedad']} %"
    )

    print(
        f"Gas: "
        f"{datos['gas']}"
    )

    print(
        f"Distancia: "
        f"{datos['distancia']} cm"
    )

    print(
        f"Luz: "
        f"{datos['luz']}"
    )

    print(
        f"\nEstado general: {estado}"
    )

    print("\nACTUADORES")

    print(
        f"Ventilador: "
        f"{actuadores['ventilador']}"
    )

    print(
        f"Alarma: "
        f"{actuadores['alarma']}"
    )

    print(
        f"Puerta: "
        f"{actuadores['puerta']}"
    )

    print(
        f"Luces: "
        f"{actuadores['luces']}"
    )

    print(
        f"Modo luces: "
        f"{actuadores['modo_luces']}"
    )

    print("===================================")


def main():

    print(
        "Iniciando sistema del edificio inteligente..."
    )

    # -----------------------------------------
    # MongoDB
    # -----------------------------------------

    base_datos = BaseDatos()

    # -----------------------------------------
    # MQTT
    # -----------------------------------------

    mqtt = ClienteMQTT()
    mqtt.conectar()

    estado_anterior = None

    try:

        while True:

            # =====================================
            # 1. LEER SENSORES
            # =====================================

            datos = leer_sensores()

            # =====================================
            # 2. DETERMINAR ESTADO
            # =====================================

            estado = obtener_estado(
                datos
            )

            # =====================================
            # 3. CONTROLAR ACTUADORES
            # =====================================

            actuadores = controlar_actuadores(
                datos,
                estado
            )

            # =====================================
            # 4. MOSTRAR INFORMACIÓN
            # =====================================

            mostrar_informacion(
                datos,
                estado,
                actuadores
            )

            # =====================================
            # 5. GUARDAR EN MONGODB
            # =====================================

            base_datos.guardar_lectura(
                datos
            )

            base_datos.guardar_estado(
                estado
            )

            # Guardamos un evento
            # únicamente cuando cambia el estado.
            if estado != estado_anterior:

                base_datos.guardar_evento(
                    "CAMBIO_ESTADO",
                    (
                        f"Estado cambiado de "
                        f"{estado_anterior} "
                        f"a {estado}"
                    )
                )

                estado_anterior = estado

            # =====================================
            # 6. PUBLICAR POR MQTT
            # =====================================

            mqtt.publicar_lecturas(
                datos
            )

            mqtt.publicar_estado(
                estado
            )

            mqtt.publicar_actuadores(
                actuadores
            )

            # =====================================
            # 7. REVISAR COMANDOS DEL DASHBOARD
            # =====================================

            comando = mqtt.obtener_comando()

            while comando is not None:

                print(
                    f"\nEjecutando comando: {comando}"
                )

                ejecutar_comando(
                    comando
                )

                base_datos.guardar_comando(
                    comando
                )

                comando = mqtt.obtener_comando()

            # =====================================
            # 8. ARM64
            # =====================================

            resultado_arm64 = agregar_temperatura(
                datos["temperatura"]
            )

            if resultado_arm64:

                print(
                    "\nResultado ARM64:"
                )

                print(
                    resultado_arm64
                )

                base_datos.guardar_resultado_arm64(
                    resultado_arm64
                )

                mqtt.publicar_resultado_arm64(
                    resultado_arm64
                )

            # =====================================
            # 9. ESPERAR
            # =====================================

            time.sleep(
                INTERVALO_LECTURA
            )

    except KeyboardInterrupt:

        print(
            "\nSistema detenido por el usuario."
        )

    finally:

        mqtt.cerrar()


if __name__ == "__main__":
    main()