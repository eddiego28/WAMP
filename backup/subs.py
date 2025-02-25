#!/usr/bin/env python3
import asyncio
import logging
import sys
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

# Configurar logging para que escriba tanto en consola como en un archivo.
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    handlers=[
        logging.StreamHandler(),            # Muestra en consola
        logging.FileHandler("subscriber.log", encoding="utf-8")  # Guarda en el archivo subscriber.log
    ]
)

# Para Windows: forzar el uso del loop selector (evita problemas con el proactor)
if sys.platform.startswith('win'):
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class JSONSubscriber(ApplicationSession):
    async def onJoin(self, details):
        print("Conexión establecida en el subscriptor (realm:", self.config.realm, ")", flush=True)

        # Función que se llamará cada vez que llegue un mensaje en el tópico suscrito
        def on_event(message):
            logging.info("Mensaje recibido: %s", message)
            print("Mensaje recibido:", message)

        # Ajusta este tópico al que tu publicador esté enviando mensajes
        topic = "com.ads.midshmi.topic"

        # Suscribirse al tópico
        await self.subscribe(on_event, topic)
        logging.info("Suscrito al tópico: %s", topic)
        print("Suscrito al tópico:", topic)

if __name__ == "__main__":
    # Ajusta la URL y el realm al que te conectas, igual que en tu publicador
    url = "ws://127.0.0.1:60001"
    realm = "default"

    runner = ApplicationRunner(url=url, realm=realm)
    runner.run(JSONSubscriber)
