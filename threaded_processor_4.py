import socket
import requests
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread
import time
from ratelimit import limits, RateLimitException, sleep_and_retry

from queue import Queue

producer_ip = "" or socket.gethostname()
producer_port = 8000
producer = socket.socket()
producer.connect((producer_ip, producer_port))

data_size = 32

cons_queue = Queue()
tpe = ThreadPoolExecutor(max_workers=30)


@sleep_and_retry
@limits(calls=10, period=1)
def process_data(data, sckt):
    # Work on data from queue
    data = data.strip().strip('\x00')
    url = f"https://pokeapi.co/api/v2/pokemon/{data}"
    t = current_thread()
    print(f"{t.name}: Processing for: {url}")
    r = requests.get(url)
    consumer_data = str(r.status_code)
    if r.ok:
        json_data = r.json()
        consumer_data += f":{json_data['name']}"
    # Work on data
    consumer_data = consumer_data.rjust(data_size, "\0")
    sckt.send(consumer_data.encode())


while True:
    data = producer.recv(data_size).decode()
    if data:
        tpe.submit(process_data, data, producer)
