import os
import math
import json
import socket
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 1099
PART_SIZE = 1024 * 16

class Peer:
    def __init__(self, host, port, folder):
        self.host = host
        self.port = port
        self.folder = folder
        self.files = self.list_files()
        
        self.socket = None
        
        self.socket_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_listen.bind((self.host, self.port))
        
        self.thread = threading.Thread(target=self.run, args=(1,), daemon=True)
        self.thread.start()

    def run(self, name):
        self.socket_listen.listen(5)
            
        for i in range(5):
            t = threading.Thread(target=self.handle_connection, args=(i,), daemon=True)
            t.start()

    def handle_connection(self, name):
        while True:
            client_socket, address = self.socket_listen.accept()
                    
            req = client_socket.recv(1024).decode()
            req = json.loads(req)

            if req["action"] == "DOWNLOAD":
                self.handle_upload(req["data"], client_socket)
                    
            client_socket.close()

    def handle_upload(self, data: dict, client_socket: socket.socket) -> None:
        if not self.check_file_exists(data["file"]):
            res = json.dumps({
                "message": "FILE_NOT_FOUND",
                "data": {
                    "host": self.host,
                    "port": self.port,
                    "number_of_parts": 0
                }            
            })
            client_socket.send(res.encode())
            
        else: # o arquivo existe
            file_path = os.path.join(self.folder, data["file"])
            file_size = os.path.getsize(file_path)
            number_of_parts = self.get_number_of_parts(file_size)

            res = json.dumps({
                "message": "FILE_FOUND",
                "data": {
                    "host": self.host,
                    "port": self.port,
                    "file_size": file_size,
                    "number_of_parts": number_of_parts
                }
            })

            client_socket.send(res.encode())

            req = client_socket.recv(1024).decode() # espera o OK do cliente
            req = json.loads(req)

            if req["message"] == "DOWNLOAD_READY":
                self.upload(file_path, number_of_parts, client_socket)
        
    def join(self, server_host, server_port):
        self.create_socket()
        self.socket.connect((server_host, server_port))

        req = json.dumps({
            "action": "JOIN",
            "data": {
                "host": self.host,
                "port": self.port,
                "files": self.files
            }
        })

        self.socket.send(req.encode())

        res = self.socket.recv(1024).decode()
        res = json.loads(res)

        if res["message"] == "JOIN_OK":
            print("\nSou peer {}:{} com arquivos {}"
                  .format(self.host, self.port, self.get_file_names(self.files))
            )

        self.socket.close()

    def update(self, file: str, server_host, server_port):
        self.create_socket()
        self.socket.connect((server_host, server_port))

        req = json.dumps({
            "action": "UPDATE",
            "data": {
                "host": self.host,
                "port": self.port,
                "file": file
            }
        })

        self.socket.send(req.encode())

        res = self.socket.recv(1024).decode()
        res = json.loads(res)

    def search(self, file: str, server_host, server_port):
        self.create_socket()
        self.socket.connect((server_host, server_port))

        req = json.dumps({
            "action": "SEARCH",
            "data": {
                "host": self.host,
                "port": self.port,
                "file": file
            }
        })

        self.socket.send(req.encode())

        res = self.socket.recv(1024).decode()
        res = json.loads(res)

        print("\npeers com arquivo solicitado: {}"
              .format(self.get_peers_info(res["data"]["peers"]))
        )

        self.socket.close()

    def download(self, host: str, port: int, file_name: str):
        self.create_socket()
        self.socket.connect((host, port))

        req = json.dumps({
            "action": "DOWNLOAD",
            "data": {
                "host": self.host,
                "port": self.port,
                "file": file_name
            }
        })

        self.socket.send(req.encode())

        res = self.socket.recv(1024).decode()
        res = json.loads(res)

        if res["message"] == "FILE_NOT_FOUND":
            print("\nArquivo não encontrado")
            return
        
        req = json.dumps({
            "message": "DOWNLOAD_READY",
            "data": {
                "host": self.host,
                "port": self.port
            }
        })

        self.socket.send(req.encode())

        file_path = os.path.join(self.folder, file_name)

        with open(file_path, "wb") as file:
            for i in range(res["data"]["number_of_parts"]):
                part = self.socket.recv(PART_SIZE)
                file.write(part)

                self.socket.send("Dados recebidos".encode())

            print("\nArquivo {} baixado com sucesso na pasta {}".format(file_name, self.folder))
            self.update(file_name, SERVER_HOST, SERVER_PORT)

    def upload(self, file_path: str, number_of_parts: int, client_socket: socket.socket) -> None:
        
        with open(file_path, "rb") as file:
            for i in range(number_of_parts):
                part = file.read(PART_SIZE)
                client_socket.send(part)
                msg = client_socket.recv(1024).decode()

    def get_number_of_parts(self, file_size: int) -> int:
        return math.ceil(file_size / PART_SIZE)

    def check_file_exists(self, file: str) -> bool:
        files = self.list_files()

        if file in files:
            return True
        
        return False

    def list_files(self) -> list:
        scan = os.scandir(self.folder)
        file_names = []

        for record in scan:
            file_names.append(record.name)

        return list(dict.fromkeys(file_names))

    def get_file_names(self, files: list) -> str:
        file_names = ""

        for file in files:
            file_names += file + " "

        return file_names.strip()
    
    def get_peers_info(self, peers: list) -> str:
        peers_info = ""

        for peer in peers:
            peers_info += "{}:{} ".format(peer[0], peer[1])

        return peers_info.strip()
    
    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == "__main__":

    peer = None
    peers = None
    file = None

    while True:
        print("\nInsira a opção da ação que deseja realizar (1, 2 ou 3): ")
        print("1 - JOIN")
        print("2 - SEARCH")
        print("3 - DOWNLOAD")

        option = input()

        while option not in ["1", "2", "3"]:
            print("Opção inválida. Tente novamente.")
            option = input()

        if option == "1": # JOIN
            print("Insira o endereco IP do peer: ", end="")
            host = input()

            print("Insira a porta do peer: ", end="")
            port = int(input())

            print("Insira a pasta onde estão os seus arquivos: ", end="")
            folder = input()

            peer = Peer(host, port, folder)

            peer.join(SERVER_HOST, SERVER_PORT)

        elif option == "2": # SEARCH
            print("Insira o nome do arquivo que deseja procurar (com extensão): ", end="")
            file = input()
            
            peer.search(file, SERVER_HOST, SERVER_PORT)

        elif option == "3": # DOWNLOAD
            print("Insira o IP do peer que possui o arquivo: ", end="")
            ip_peer = input()

            print("Insira a porta do peer que possui o arquivo: ", end="")
            port_peer = int(input())

            peer.download(ip_peer, port_peer, file)
