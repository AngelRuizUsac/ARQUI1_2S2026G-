import json
from queue import Queue, Empty

import paho.mqtt.client as mqtt

from configuracion import (MQTT_ACTIVO,MQTT_BROKER,MQTT_PUERTO,MQTT_USUARIO,MQTT_PASSWORD,MQTT_TLS,IDENTIFICADOR_UNICO)


class ClienteMQTT:

    def __init__(self):

        self.activo = MQTT_ACTIVO
        self.cliente = None

        # Aquí se guardan los comandos enviados desde el dashboard
        self.comandos = Queue()


    def conectar(self):

        if not self.activo:
            print("MQTT desactivado.")
            return

        try:

            self.cliente = mqtt.Client()

            self.cliente.on_connect = self._al_conectar
            self.cliente.on_message = self._al_recibir_mensaje

            if MQTT_USUARIO:
                self.cliente.username_pw_set(MQTT_USUARIO,MQTT_PASSWORD)

            if MQTT_TLS:
                self.cliente.tls_set()

            self.cliente.connect(MQTT_BROKER,MQTT_PUERTO,60)

            self.cliente.loop_start()

            print("Conectando con MQTT...")

        except Exception as error:

            print(f"Error al conectar con MQTT: {error}")

            self.activo = False


    def _topic(self, ruta):

        return (f"{IDENTIFICADOR_UNICO}/"f"edificio/{ruta}")


    def _al_conectar(self,cliente,userdata,flags,codigo):

        if codigo == 0:

            print("Conexión MQTT establecida.")

            cliente.subscribe(self._topic("control/remoto"))

        else:

            print(f"Error MQTT. Código: {codigo}")


    def _al_recibir_mensaje(self,cliente,userdata,mensaje):

        try:

            contenido = mensaje.payload.decode()

            comando = json.loads(contenido)

            self.comandos.put(comando)

            print(f"Comando MQTT recibido: {comando}")

        except Exception as error:

            print(f"Error al leer comando MQTT: {error}")


    def publicar(self, ruta, datos):

        if not self.activo:
            return

        mensaje = json.dumps(datos,ensure_ascii=False)

        self.cliente.publish(self._topic(ruta),mensaje)


    def publicar_lecturas(self, datos):

        self.publicar("sensores/temperatura",{"valor": datos["temperatura"]})

        self.publicar("sensores/humedad",{"valor": datos["humedad"]})

        self.publicar("sensores/gas",{"valor": datos["gas"]})

        self.publicar("sensores/distancia",{"valor": datos["distancia"]})

        self.publicar("sensores/luz",{"valor": datos["luz"]})


    def publicar_estado(self, estado):

        self.publicar("estado/global",{"estado": estado})


    def publicar_actuadores(self, actuadores):

        self.publicar("actuadores/puerta",{"estado": actuadores["puerta"]})

        self.publicar(
            "actuadores/luces",
            {"estado": actuadores["luces"],"modo": actuadores["modo_luces"]})

        self.publicar("actuadores/ventilador",{"estado": actuadores["ventilador"]})

        self.publicar("actuadores/alarma",{"estado": actuadores["alarma"]})


    def publicar_resultado_arm64(self, resultado):

        self.publicar("arm64/resultados",resultado)


    def obtener_comando(self):

        try:
            return self.comandos.get_nowait()

        except Empty:
            return None


    def cerrar(self):

        if self.activo and self.cliente:

            self.cliente.loop_stop()

            self.cliente.disconnect()