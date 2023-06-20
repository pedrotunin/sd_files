import os
import json
import socket

class Peer:
    def __init__(self, host, port, folder):
        self.host = host
        self.port = port
        self.folder = folder
        self.files = self.list_files()
        self.socket = None

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

    def update(self):
        #TODO: implementar update no servidor
        pass

    def search(self, file: str, server_host, server_port):
        self.create_socket()
        self.socket.connect((server_host, server_port))

        req = json.dumps({
            "action": "SEARCH",
            "data": {
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

    def download(self, host: str, port: int, file: str):
        #TODO: implementar requisição de download de arquivos para outros peers
        pass

    def upload(self, host: str, port: str, file: str):
        #TODO: implementar upload de arquivos para outros peers
        pass

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
        self.socket.bind((self.host, self.port))

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
            folder = "/home/tunin/sd_files/projeto1/peer_files/" + input()

            peer = Peer(host, port, folder)

            peer.join("127.0.0.1", 1099)

        elif option == "2": # SEARCH
            print("Insira o nome do arquivo que deseja procurar (com extensão): ", end="")
            file = input()
            
            peer.search(file, "127.0.0.1", 1099)

        elif option == "3": # DOWNLOAD
            print("Insira o IP do peer que possui o arquivo: ")
            ip_peer = "127.0.0.1" #input()

            print("Insira a porta do peer que possui o arquivo: ")
            port_peer = 12346 #int(input())

            peer.download(ip_peer, port_peer, file)
