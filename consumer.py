import socket

ip = "" or socket.gethostname()
port = 8001
data_size = 32


def consumer():
    s = socket.socket()
    s.bind((ip, port))
    s.listen(10)
    try:
        while True:
            client, addr = s.accept()
            print(f"Got connection from {addr}")
            while True:
                data = client.recv(data_size).decode()
                if data:
                    print(f"Data received: {data}")
                else:
                    client.close()
                    break
    except KeyboardInterrupt:
        print("Exiting Consumer")
    finally:
        s.close()


if __name__ == "__main__":
    consumer()
