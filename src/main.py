#!../.venv/bin/python

import json

import trio
import httpx

with open('../../_keys/kucoin.json') as f:
    keys = json.load(f)

print(keys)

from SocketBase import SocketBase

from uuid import uuid4

import hmac
import base64
import hashlib

from time import time
from urllib.parse import urlencode

import arrow


def gen_uuid():
    return str(uuid4()).replace('-', '')


class RestAPI():
    def __init__(self, keys):
        self.keys = keys
        self.url_base = 'https://api.kucoin.com'

        self.client = httpx.AsyncClient(http2=True)

    async def send(self, method, uri, **kwargs):
        now_time = int(time() * 1000)

        if method in 'GET DELETE'.split():
            if qs := urlencode(**kwargs):
                uri += '?' + qs

        secret, passphrase = self.keys['api_secret'], self.keys['api_passphrase']

        sign = lambda message: base64.b64encode(
            hmac.new(
                secret.encode(),
                message.encode(),
                hashlib.sha256
            ).digest()
        )

        headers = {
            'KC-API-SIGN':          sign(str(now_time) + method + uri),
            'KC-API-TIMESTAMP':          str(now_time),
            'KC-API-KEY':           self.keys['api_key'],
            'KC-API-PASSPHRASE':    sign(passphrase),
            'Content-Type':         'application/json',
            'KC-API-KEY-VERSION':   '2',
            'User-Agent':           'pi-v3.14'
        }

        url = f'{self.url_base}{uri}'

        if method == 'GET':
            response = await self.client.get(url, headers=headers)

        if method == 'POST':
            response = await self.client.post(url, headers=headers, data=json.dumps(kwargs) if kwargs else '')

        if response.status_code != 200:
            raise Exception(f'ERROR [{response.status_code}] {response.text}')
        else:
            return response.json()['data']


async def amain():
    api = RestAPI(keys)

    r = await api.send('POST', '/api/v1/bullet-private')

    endpoint = r['instanceServers'][0]['endpoint']
    token = r['token']
    connectId = gen_uuid()

    async def on_msg(msg):
        print('MESSAGE', type(msg), msg)

    sock = SocketBase(
        ws_url=f'{endpoint}?token={token}&connectId={connectId}',
        on_msg=on_msg,
        sendfunc=SocketBase.to_str,
        recvfunc=SocketBase.str_to_json
    )

    async with trio.open_nursery() as n:
        n.start_soon(sock.run_blocking)

        await sock.ready.wait()

        print('READY')

        J = {
            "id": gen_uuid(),
            "type": "subscribe",
            "topic": "/market/ticker:BTC-USDT,ETH-USDT",
            "privateChannel": False,
            "response": False
        }
        await sock.send(J)

    while True:
        print('loopy')
        await trio.sleep(1)


trio.run(amain)