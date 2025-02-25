#!/usr/bin/env python3
import asyncio
import json
import logging
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

# Activamos el logging para depurar
logging.basicConfig(level=logging.DEBUG)

class JSONPublisherWS(ApplicationSession):
    async def onJoin(self, details):
        print("Conexión establecida en el publicador", flush=True)
        while True:
            try:
                # Se abre y lee el archivo JSON
                with open(r"C:\Users\ededi\Documents\PROYECTOS\WAMP\publisher\data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print("Error al leer el archivo JSON:", e, flush=True)
                self.leave()
                return

            # Se publica el contenido del JSON en el tópico 'com.ads.midshmi.topic'
            self.publish("com.ads.midshmi.topic", data)
            print("Mensaje publicado:", data, flush=True)
            await asyncio.sleep(2)  # Publica cada 2 segundos

if __name__ == '__main__':
    # Conexión al broker por WebSocket en el puerto 600001 y la ruta /ws, realm "ADS.MIDSHMI"
    runner = ApplicationRunner(url="ws://127.0.0.1:60001", realm="default")
    runner.run(JSONPublisherWS)
