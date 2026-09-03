from datetime import datetime, timezone

from pymongo import MongoClient

from configuracion import (MONGO_ACTIVO,MONGO_URI,MONGO_BASE_DATOS)


class BaseDatos:

    def __init__(self):

        self.activa = MONGO_ACTIVO
        self.base_datos = None

        if not self.activa:
            print("MongoDB desactivado.")
            return

        try:

            cliente = MongoClient(MONGO_URI)
            self.base_datos = cliente[MONGO_BASE_DATOS]
            print("Conexión con MongoDB establecida.")

        except Exception as error:

            print(f"Error al conectar con MongoDB: {error}")
            self.activa = False


    def guardar_lectura(self, datos):

        if not self.activa:
            return

        documento = datos.copy()

        documento["timestamp"] = datetime.now(timezone.utc)

        self.base_datos.sensor_readings.insert_one(documento)


    def guardar_evento(self, tipo, mensaje):

        if not self.activa:
            return

        self.base_datos.events.insert_one({"tipo": tipo,"mensaje": mensaje,"timestamp": datetime.now(timezone.utc)})


    def guardar_comando(self, comando):

        if not self.activa:
            return

        documento = comando.copy()

        documento["timestamp"] = datetime.now(timezone.utc)

        self.base_datos.commands.insert_one(documento)


    def guardar_estado(self, estado):

        if not self.activa:
            return

        self.base_datos.system_status.update_one({"_id": "estado_actual"},{"$set": {"estado": estado,"timestamp": datetime.now(timezone.utc)}},upsert=True)


    def guardar_resultado_arm64(self, resultado):

        if not self.activa:
            return

        documento = resultado.copy()

        documento["timestamp"] = datetime.now(timezone.utc)

        self.base_datos.arm64_results.insert_one(documento)