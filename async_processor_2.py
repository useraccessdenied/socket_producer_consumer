import asyncio
import socket
import aiohttp
import time

producer_ip = "" or socket.gethostname()
producer_port = 8000
consumer_ip = "" or socket.gethostname()
consumer_port = 8001
data_size = 32


async def async_http_get(data):
    async with aiohttp.ClientSession() as http:
        url = f"https://pokeapi.co/api/v2/pokemon/{data}"
        async with http.get(url) as r:
            code = r.status
            json = await r.json()
            name = json['name']
            data = f"{code}:{name}"
            return data


async def worker(queue, consumer_writer):
    while True:
        data = await queue.get()
        http_data = await async_http_get(data)
        print(f"Sending ({data}): {http_data}")
        consumer_writer.write(http_data.encode())
        await consumer_writer.drain()
        queue.task_done()


async def async_processor():
    producer_reader, producer_writer = await asyncio.open_connection(producer_ip, producer_port)
    consumer_reader, consumer_writer = await asyncio.open_connection(consumer_ip, consumer_port)

    queue = asyncio.Queue()

    while True:
        data = await producer_reader.read(data_size)
        data = data.decode()
        data = data.strip().strip('\x00')

        if data:
            await queue.put(data)
        else:
            producer_writer.close()
            await producer_writer.wait_closed()
            break

    workers = []

    for _ in range(30):
        task = asyncio.create_task(worker(queue, consumer_writer))
        workers.append(task)

    # Wait until queue is processed
    await queue.join()

    for task in workers:
        task.cancel()

    try:
        await asyncio.gather(*workers)
    except asyncio.CancelledError:
        print("All worker tasks are cancelled!")

    consumer_writer.close()
    await consumer_writer.wait_closed()


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(async_processor())
    print(f"Total time taken: {time.time() - start_time}")
