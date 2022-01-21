# Minimal Async KuCoin REST API + WebSocket using trio

Coded by π (pi@pipad.org TG: @pipad)
22 January 2022

KuCoin needs an async Python client

This code may serve as a foundation for an async Python KuCoin API.

Publishing it is an invitation for others to build upon a solid foundation.
You are welcome to build it out.
Just please, keep it clean and do your best to balance all forces: abstraction, functionality, clarity, ...


# What this code does

The two wings are: REST API (via httpx) and WebSocket Client (via trio-websocket)

This minimal example demonstrates both wings.

It fetches a websocket token (which requires a REST API call) and connects to a websocket.


# How to get it running

```
> pip install arrow trio trio-websocket httpx[http2]
```

Also create a kucoin.json file:
```
{
    "api_key": "...",
    "api_secret": "...",
    "api_passphrase": "..."
}
```

To run:
```
python main.py
```


# on trio vs asyncio

For network-centric programming threads are the past, async is the future.

However, asyncio (the Python stdlib offering) is a mess. 
It evolved gradually as Python developed concepts of async programming.
It is therefore stuck with the burden of backward compatibility with itself.
asyncio code is hard to read, hard to write, hard to debug, hard to maintain.

trio is a beautiful from-the-ground-up async library that has learned from the mistakes of asyncio.
It is clean, intuitive and sports a vibrant gitter community.

We should all be using trio, and asyncio should be thanked for its efforts and put to rest.
