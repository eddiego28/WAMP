#!/usr/bin/env python3
import os, sys, json, asyncio, threading, logging, datetime
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Cada ejecución crea un archivo de log nuevo con fecha y hora hasta segundos.
LOG_FILENAME = os.path.join(os.getcwd(), "log" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt")
msgLogger = logging.getLogger("msgLogger")
msgLogger.setLevel(logging.INFO)
for handler in msgLogger.handlers[:]:
    msgLogger.removeHandler(handler)
fileHandler = logging.FileHandler(LOG_FILENAME, encoding="utf-8")
fileHandler.setFormatter(logging.Formatter("%(message)s"))
msgLogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
msgLogger.addHandler(consoleHandler)

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
        content = {"message": kwargs.get("message", None) or args}
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
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
