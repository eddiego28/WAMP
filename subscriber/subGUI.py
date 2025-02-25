#!/usr/bin/env python3
import os
import asyncio
import threading
import logging
import sys
import json
import datetime
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Usar la misma ruta fija para el log
LOG_DIR = r"C:\Users\ededi\Documents\PROYECTOS\WAMP"
LOG_FILENAME = os.path.join(LOG_DIR, "log" + datetime.datetime.now().strftime("%Y-%m-%d") + ".txt")

msgLogger = logging.getLogger("msgLogger")
msgLogger.setLevel(logging.INFO)
for handler in msgLogger.handlers[:]:
    msgLogger.removeHandler(handler)
fh = logging.FileHandler(LOG_FILENAME, encoding="utf-8")
fh.setFormatter(logging.Formatter("%(message)s"))
msgLogger.addHandler(fh)

class MultiTopicSubscriber(ApplicationSession):
    def __init__(self, config, topics, on_message_callback=None):
        super().__init__(config)
        self.topics = topics
        self.on_message_callback = on_message_callback
        self.keep_alive = None

    async def onJoin(self, details):
        logging.info("Subscriptor: Conexión establecida en realm: %s", self.config.realm)
        for topic in self.topics:
            try:
                await self.subscribe(self.on_event, topic)
                logging.info("Subscriptor: Suscrito al tópico: %s", topic)
            except Exception as e:
                logging.error("Subscriptor: Error al suscribirse a %s: %s", topic, e)
        self.keep_alive = asyncio.Future()
        try:
            await self.keep_alive
        except asyncio.CancelledError:
            pass

    def on_event(self, *args, **kwargs):
        content = {"args": args, "kwargs": kwargs}
        log_entry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "header": "Sys answer",
            "message": content
        }
        msgLogger.info(json.dumps(log_entry, ensure_ascii=False, indent=2))
        logging.info("Subscriptor: Evento recibido: %s", content)
        if self.on_message_callback:
            self.on_message_callback(content)

def start_subscriber(url, realm, topics, on_message_callback=None):
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        runner = ApplicationRunner(url=url, realm=realm)
        runner.run(lambda config: MultiTopicSubscriber(config, topics, on_message_callback))
    threading.Thread(target=run, daemon=True).start()
