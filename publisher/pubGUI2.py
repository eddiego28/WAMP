#!/usr/bin/env python3
import os
import json
import asyncio
import threading
import logging
import sys
import datetime
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Usar el directorio de trabajo actual para el log (o la ruta fija que hayas definido)
LOG_DIR = os.getcwd()  # O sustituye por una ruta fija, si tienes permisos.
LOG_FILENAME = os.path.join(LOG_DIR, "log" + datetime.datetime.now().strftime("%Y-%m-%d") + ".txt")

msgLogger = logging.getLogger("msgLogger")
msgLogger.setLevel(logging.INFO)
for handler in msgLogger.handlers[:]:
    msgLogger.removeHandler(handler)
fh = logging.FileHandler(LOG_FILENAME, encoding="utf-8")
fh.setFormatter(logging.Formatter("%(message)s"))
msgLogger.addHandler(fh)

global_session = None
global_loop = None

class JSONPublisher(ApplicationSession):
    def __init__(self, config, topic):
        super().__init__(config)
        self.topic = topic
        self.keep_alive = None

    async def onJoin(self, details):
        global global_session, global_loop
        global_session = self
        global_loop = asyncio.get_event_loop()
        logging.info("Publicador: Conexión establecida en realm: %s", self.config.realm)
        self.keep_alive = asyncio.Future()
        try:
            await self.keep_alive
        except asyncio.CancelledError:
            pass

    async def onLeave(self, details):
        if self.keep_alive and not self.keep_alive.done():
            self.keep_alive.cancel()
        await super().onLeave(details)

def start_publisher(url, realm, topic):
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        runner = ApplicationRunner(url=url, realm=realm)
        runner.run(lambda config: JSONPublisher(config, topic))
    threading.Thread(target=run, daemon=True).start()

def send_message_now(topic, message, delay=0):
    """
    Envía 'message' en 'topic' con retraso 'delay' (segundos) y
    registra en el log un objeto JSON con:
      - timestamp
      - header: "Stimulus message"
      - message
    """
    global global_session, global_loop
    if global_session is None or global_loop is None:
        logging.error("Publicador: No hay sesión activa. Inicia el publicador primero.")
        return
    async def _send():
        if delay > 0:
            await asyncio.sleep(delay)
        global_session.publish(topic, message)
        log_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "header": "Stimulus message",
            "message": message
        }
        msgLogger.info(json.dumps(log_entry, ensure_ascii=False, indent=2))
        logging.info("Publicador: Mensaje enviado en %s", topic)
    asyncio.run_coroutine_threadsafe(_send(), global_loop)
