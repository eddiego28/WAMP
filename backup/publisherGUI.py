#!/usr/bin/env python3
import json
import asyncio
import threading
import logging
import sys
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

# Para Windows: forzar el uso del loop selector (evita problemas con el proactor)
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.DEBUG)

# Variable global para el mensaje personalizado.
# Si es None, se leerá el archivo data.json.
global_message_data = None

class JSONPublisher(ApplicationSession):
    def __init__(self, topic, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.topic = topic

    async def onJoin(self, details):
        print("Conexión establecida en el publicador (realm:", self.config.realm, ")", flush=True)
        while True:
            if global_message_data is not None:
                data = global_message_data
            else:
                try:
                    with open(r"C:\Users\ededi\Documents\PROYECTOS\WAMP\publisher\data.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception as e:
                    print("Error al leer data.json:", e, flush=True)
                    self.leave()
                    return
            self.publish(self.topic, data)
            print("Mensaje publicado en", self.topic, ":", data, flush=True)
            await asyncio.sleep(2)

def start_publisher(url, realm, topic):
    """
    Inicia el publicador en un hilo separado.
      - url: URL de conexión (ej. "ws://127.0.0.1:60001")
      - realm: Realm a usar
      - topic: Tópico en el que publicar
    """
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        runner = ApplicationRunner(url=url, realm=realm)
        runner.run(lambda *args, **kwargs: JSONPublisher(topic, *args, **kwargs))
    threading.Thread(target=run, daemon=True).start()
