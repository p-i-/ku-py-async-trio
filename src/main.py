#!../.venv/bin/python

# stdlib
import json
from uuid import uuid4

# 3rd party
import arrow
import trio

# ours
from SocketBase import SocketBase
from RestAPI import RestAPI


def gen_uuid():
    return str(uuid4()).replace('-', '')


async def amain():
    with open('../../_keys/kucoin.json') as f:
        keys = json.load(f)

    print(keys)

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