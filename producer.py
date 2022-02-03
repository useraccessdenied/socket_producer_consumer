import random
import string
import socket
import time

ip = "" or socket.gethostname()
port = 8000
data_size = 32


def len_diff(s):
    return data_size - len(s)


def producer():
    s = socket.socket()
    s.bind((ip, port))
    s.listen(10)
    try:
        while True:
            client, addr = s.accept()
            print(f"Got connection from {addr}")
            for i in range(100):
                data = f"{random.randint(1, 100)}"
                data = data.rjust(data_size, "\0")

                # time.sleep(random.random())
                client.send(data.encode())
            client.close()
    except KeyboardInterrupt:
        print("Exiting Producer")
    finally:
        s.close()


if __name__ == "__main__":
    producer()
