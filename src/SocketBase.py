import json
import gzip
import traceback

import trio
from trio_websocket import open_websocket_url

import logging
logger = logging.getLogger('trio-websocket').setLevel(logging.WARNING)


class SocketBase:
    KEEPALIVE_INTERVAL_S = 10

    @staticmethod
    def gzbytes_to_json(gzipped_bytes):
        as_bytes = gzip.decompress(gzipped_bytes)
        as_string = as_bytes.decode('utf8')
        as_json = json.loads(as_string)
        return as_json


    @staticmethod
    def str_to_json(str):
        return json.loads(str)


    @staticmethod
    def to_str(x):
        return json.dumps(x) if isinstance(x,dict) else str(x)


    def __init__(self, ws_url, on_msg, keepalive=True, recvfunc=lambda x:x, sendfunc=lambda x:x):
        self.ws_url = ws_url
        self.on_msg = on_msg
        self.keepalive = keepalive
        self.recvfunc = recvfunc
        self.sendfunc = sendfunc

        self.ready = trio.Event()


    async def run_blocking(self):
        with open('log.txt', 'w') as fd:
            fd.write('[\n')
            while True:
                try:
                    async with open_websocket_url(self.ws_url) as sock:
                        print(f'{self.ws_url} connected')
                        self.sock = sock

                        async with trio.open_nursery() as nursery:
                            self.nursery = nursery

                            async def recv():
                                self.ready.set()
                                while True:
                                    # to make sure we regularly hit checkpoints we could do:
                                    #     with trio.move_on_after(5):
                                    msg = await sock.get_message()
                                    decoded = self.recvfunc(msg)
                                    fd.write(str(decoded) + ',\n')
                                    await self.on_msg(decoded)

                            nursery.start_soon(recv)

                            if self.keepalive:
                                async def keepalive():
                                    while True:
                                        print('sending ping')
                                        await sock.ping()
                                        await trio.sleep(SocketBase.KEEPALIVE_INTERVAL_S)
                                        print('sent ping')

                                nursery.start_soon(keepalive)

                            self.ready.set()

                except Exception as e:
                    print('⛔️ WebSocket disconnect')
                    print(e)
                    traceback.print_exc()

                await trio.sleep(5)
                print('Attempting reconnect')

            print('👋 from websocket')


    async def send(self, msg):
        await self.sock.send_message(self.sendfunc(msg))
