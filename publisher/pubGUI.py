#!/usr/bin/env python3
import json
import asyncio
import threading
import logging
import sys
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

# Configurar logging para que escriba tanto en consola como en un archivo.
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    handlers=[
        logging.StreamHandler(),  # Muestra en consola
        logging.FileHandler("messages.log", encoding="utf-8")  # Guarda en el archivo sistema.log
    ]
)


# Para Windows: forzar el uso del loop selector (evita problemas con el proactor)
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(level=logging.DEBUG)

# Variables globales para almacenar la sesión y el loop del publicador.
global_session = None
global_loop = None

class JSONPublisher(ApplicationSession):
    # La fábrica recibe 'config' y luego el topic que configuramos.
    def __init__(self, config, topic):
        super().__init__(config)
        self.topic = topic

    async def onJoin(self, details):
        global global_session, global_loop
        global_session = self
        global_loop = asyncio.get_event_loop()
        print("Conexión establecida en el publicador (realm:", self.config.realm, ")", flush=True)
        # Mantener la sesión activa indefinidamente
        await asyncio.Future()

def start_publisher(url, realm, topic):
    """
    Inicia el publicador en un hilo separado.
      - url: URL de conexión (ej. "ws://127.0.0.1:60001")
      - realm: Realm a usar.
      - topic: Tópico base para enviar los mensajes.
    """
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        runner = ApplicationRunner(url=url, realm=realm)
        runner.run(lambda config: JSONPublisher(config, topic))
    threading.Thread(target=run, daemon=True).start()

def send_message_now(topic, message, delay=0):
    """
    Programa el envío del mensaje en el topic indicado, con el delay (en segundos).
    """
    global global_session, global_loop
    if global_session is None or global_loop is None:
        print("No hay sesión activa. Asegúrate de iniciar el publicador primero.")
        return
    async def _send():
        if delay > 0:
            await asyncio.sleep(delay)
        global_session.publish(topic, message)
        logging.info("Mensaje enviado en %s: %s", topic, message)
        print("Mensaje enviado en", topic, ":", message)
    asyncio.run_coroutine_threadsafe(_send(), global_loop)
