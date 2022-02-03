import socket
import requests
import time

producer_ip = "" or socket.gethostname()
producer_port = 8000
consumer_ip = "" or socket.gethostname()
consumer_port = 8001
data_size = 32


def processor():
    try:

        producer = socket.socket()
        producer.connect((producer_ip, producer_port))
        consumer = socket.socket()
        consumer.connect((consumer_ip, consumer_port))

        while True:
            data = producer.recv(data_size).decode()
            if data:
                data = data.strip().strip('\x00')
                url = f"https://pokeapi.co/api/v2/pokemon/{data}"
                print(f"Processing for {data}: {url}")
                r = requests.get(url)
                consumer_data = str(r.status_code)
                if r.ok:
                    json_data = r.json()
                    consumer_data += f":{json_data['name']}"
                consumer.send(f"{consumer_data}".encode())
            else:
                producer.close()
                consumer.close()
                break

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


