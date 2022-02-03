import socket
import requests
from threading import Thread, Event
import time
from signal import signal, SIGINT, SIGTERM, raise_signal
from queue import Queue

producer_ip = "" or socket.gethostname()
producer_port = 8000
consumer_ip = "" or socket.gethostname()
consumer_port = 8001
data_size = 32

prod_queue = Queue()
cons_queue = Queue()


class ServiceExit(Exception):
    """
    This class is purely used to trigger end of program
    execution by simulating failure.
    """
    pass


def shutdown_service(signum, frame):
    print("Interrupt signal received")
    raise ServiceExit


class GetFromProducerThread(Thread):
    """
    This Thread reads data from Producer and puts it
    into processing queue
    """

    def __init__(self):
        Thread.__init__(self)
        # This flag tracks shutdown event from main thread
        self.shutdown_flag = Event()
        self.name = "GetFromProducerThread"

    def run(self) -> None:
        print("Reading from producer started.")
        producer = socket.socket()
        producer.connect((producer_ip, producer_port))

        while not self.shutdown_flag.is_set():
            while True:
                data = producer.recv(data_size).decode()
                if data:
                    data = data.strip().strip('\x00')
                    prod_queue.put(data)
                else:
                    time.sleep(0.5)
                    break
            time.sleep(0.5)

        producer.close()
        print("Reading from producer stopped.")


class WorkerThread(Thread):
    """
    This Thread reads data from Queue and starts
    processing it. Then puts result into prod_queue
    """

    def __init__(self):
        Thread.__init__(self)
        # This flag tracks shutdown event from main thread
        self.shutdown_flag = Event()

    def run(self) -> None:
        while not self.shutdown_flag.is_set():
            while True:
                if not prod_queue.empty():
                    data = prod_queue.get_nowait()
                    url = f"https://pokeapi.co/api/v2/pokemon/{data}"
                    print(f"{self.name}: Processing for {data}: {url}")
                    r = requests.get(url)
                    consumer_data = str(r.status_code)
                    if r.ok:
                        json_data = r.json()
                        consumer_data += f":{json_data['name']}"
                    cons_queue.put(f"{consumer_data}")
                else:
                    time.sleep(0.5)
                    break

            time.sleep(0.5)


class SendToConsumerThread(Thread):
    """
    This Thread reads data from Queue and sends it
    to Consumer port
    """

    def __init__(self):
        Thread.__init__(self)
        # This flag tracks shutdown event from main thread
        self.shutdown_flag = Event()
        self.name = "SendToConsumerThread"

    def run(self) -> None:
        print("Sending to Consumer started.")
        consumer = socket.socket()
        consumer.connect((consumer_ip, consumer_port))

        while not self.shutdown_flag.is_set():
            while True:
                if not cons_queue.empty():
                    data = cons_queue.get_nowait()
                    data = data.rjust(data_size, "\0")
                    consumer.send(f"{data}".encode())
                else:
                    time.sleep(0.5)
                    break
            time.sleep(0.5)

        consumer.close()
        print("Sending to Consumer stopped.")


def processor():
    signal(SIGINT, shutdown_service)
    signal(SIGTERM, shutdown_service)

    get_from_prod_thread = GetFromProducerThread()
    send_to_cons_thread = SendToConsumerThread()
    worker_threads = []
    total_workers = 30

    try:

        get_from_prod_thread.start()
        send_to_cons_thread.start()

        for i in range(total_workers):
            worker = WorkerThread()
            worker.name = f"Worker_{i}"
            worker_threads.append(worker)
            worker.start()

        # Pause the main thread until workers are running
        while True:
            time.sleep(0.5)

    except ServiceExit:
        get_from_prod_thread.shutdown_flag.set()
        send_to_cons_thread.shutdown_flag.set()
        print("Completing pending operations.\nPlease wait.")
        get_from_prod_thread.join()
        send_to_cons_thread.join()
        for w in worker_threads:
            w.shutdown_flag.set()
            w.join()

    except ConnectionRefusedError:
        print("Server not running!")
    except ConnectionResetError:
        print("Connection got broken!")
    except ConnectionError:
        print("Unable to establish connection!")


if __name__ == "__main__":
    start_time = time.time()
    processor()
    print(f"Total time taken: {time.time() - start_time}")
