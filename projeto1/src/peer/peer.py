import os
import sys
import socket

class Peer:
    def __init__(self, host, port, folder):
        self.host = host
        self.port = port
        self.folder = folder
        self.files = self.list_files()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def join(self):
        #TODO: implementar join no servidor
        pass

    def update(self):
        #TODO: implementar update no servidor
        pass

    def search(self, file: str) -> list:
        #TODO: implementar busca por arquivos no servidor
        pass

    def download(self, host: str, port: int, file: str):
        #TODO: implementar requisição de download de arquivos para outros peers
        pass

    def upload(self, host: str, port: str, file: str):
        #TODO: implementar upload de arquivos para outros peers
        pass

    def list_files(self) -> list:
        scan = os.scandir(self.folder)
        file_names = []

        for record in scan:
            file_names.append(record.name)

        return list(dict.fromkeys(file_names))

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
            print("Insira o endereco IP do peer: ")
            host = "127.0.0.1" #input()

            print("Insira a porta do peer: ")
            port = 12345 #int(input())

            print("Insira a pasta onde estão os seus arquivos: ")
            folder = "/home/tunin/sd_files/projeto1/peer_files/1" #input()

            peer = Peer(host, port, folder)

            peer.join()

        elif option == "2": # SEARCH
            print("Insira o nome do arquivo que deseja procurar (com extensão): ")
            file = "metallica.mp4" #input()
            
            peers = peer.search(file)

        elif option == "3": # DOWNLOAD
            print("Insira o IP do peer que possui o arquivo: ")
            ip_peer = "127.0.0.1" #input()

            print("Insira a porta do peer que possui o arquivo: ")
            port_peer = 12346 #int(input())

            peer.download(ip_peer, port_peer, file)
