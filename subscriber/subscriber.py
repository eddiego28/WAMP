#!/usr/bin/env python3
import asyncio
import logging
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner

# Activar logging para ver información de depuración
logging.basicConfig(level=logging.DEBUG)

class JSONSubscriberWS(ApplicationSession):
    async def onJoin(self, details):
        print("Conexión establecida en el suscriptor", flush=True)

        # Callback que se ejecutará al recibir un mensaje
        def on_event(data):
            print("Mensaje recibido:", data, flush=True)

        # Suscribirse al tópico 'com.ads.midshmi.topic'
        await self.subscribe(on_event, "com.ads.midshmi.topic")
        print("Suscripción realizada al tópico 'com.ads.midshmi.topic'", flush=True)

if __name__ == '__main__':
    # Conectar al broker mediante WebSocket en ws://127.0.0.1:600001/ws
    runner = ApplicationRunner(url="ws://127.0.0.1:60001", realm="default")
    runner.run(JSONSubscriberWS)