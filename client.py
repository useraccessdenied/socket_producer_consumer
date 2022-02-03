import socket

server_ip = "" or socket.gethostname()
server_port = 9000
data_size = 32


def client():
    try:

        s = socket.socket()
        s.connect((server_ip, server_port))
        while True:
            data = s.recv(data_size).decode()
            if data:
                print(f"Data received: {data}")
            else:
                break

    except ConnectionRefusedError:
        print("Server not running!")
    except ConnectionResetError:
        print("Connection got broken!")
    except ConnectionError:
        print("Unable to establish connection!")


if __name__ == "__main__":
    client()
