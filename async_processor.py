import asyncio
import socket
import aiohttp
import time

producer_ip = "" or socket.gethostname()
producer_port = 8000
consumer_ip = "" or socket.gethostname()
consumer_port = 8001
data_size = 32


async def async_processor():
    producer_reader, producer_writer = await asyncio.open_connection(producer_ip, producer_port)
    consumer_reader, consumer_writer = await asyncio.open_connection(consumer_ip, consumer_port)

    while True:
        data = await producer_reader.read(data_size)
        data = data.decode()
        data = data.strip().strip('\x00')

        if data:
            print(f"Data received: {data}")

            async with aiohttp.ClientSession() as http:
                url = f"https://pokeapi.co/api/v2/pokemon/{data}"
                async with http.get(url) as r:
                    code = r.status
                    json = await r.json()
                    name = json['name']
                    data = f"{code}:{name}"

            consumer_writer.write(data.encode())
            # await consumer_writer.drain()
        else:
            producer_writer.close()
            await producer_writer.wait_closed()
            consumer_writer.close()
            await consumer_writer.wait_closed()
            break


if __name__ == "__main__":
    start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_processor())
    print(f"Total time taken: {time.time() - start_time}")
