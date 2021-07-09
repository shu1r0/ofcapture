import asyncio

loop = asyncio.get_event_loop()

# class Client(object):
#
#     def __init__(self, name, loop):
#         self.name = name
#         self.loop = loop
#
#     def __await__(self):
#         r, w = yield from asyncio.open_connection("127.0.0.1", 6666, loop=self.loop)
#         yield from asyncio.sleep(5)
#         return 0

async def main(name, loop):
    print('chunk reader')
    r, w = await asyncio.open_connection("127.0.0.1", 63333, loop=loop)
    w.write(name.encode())
    await w.drain()
    await asyncio.sleep(5)
    data = await r.read(2048)
    print(data)
    w.close()
    print("end")

async def main_10times(loop):
    times = 10
    for i in range(times):
        name = "s"+str(i)
        asyncio.ensure_future(main(name, loop))
        await asyncio.sleep(1)
    await asyncio.sleep(5*times + 1*times + 2)


if __name__ == "__main__":
    loop.run_until_complete(main_10times(loop))
    loop.close()

