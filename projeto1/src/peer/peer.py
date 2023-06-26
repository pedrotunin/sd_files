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
        self.files = self.list_files() # lista de arquivos que o peer possui
        
        self.socket = None
        
        # cria um socket para escutar por novas conexões de outros peers
        self.socket_listen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_listen.bind((self.host, self.port))
        
        # iniciada thread para escutar por novas conexões de outros peers
        self.thread = threading.Thread(target=self.run, args=(1,), daemon=True)
        self.thread.start()

    # função que fica escutando por novas conexões de outros peers
    def run(self, name):
        self.socket_listen.listen(5)
            
        # cria 10 threads para lidar com as conexões
        for i in range(10):
            t = threading.Thread(target=self.handle_connection, args=(i,), daemon=True)
            t.start()

    # função que lida com a conexão de um peer e encaminha a requisição para a função correta
    def handle_connection(self, name):
        while True:
            client_socket, address = self.socket_listen.accept()
                    
            req = client_socket.recv(1024).decode()
            req = json.loads(req)

            if req["action"] == "DOWNLOAD":
                self.handle_upload(req["data"], client_socket)
                    
            client_socket.close()

    # função que trata a requisição de download de um arquivo
    def handle_upload(self, data: dict, client_socket: socket.socket) -> None:

        # se o arquivo não existe, envia uma mensagem de erro para o peer
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
            file_size = os.path.getsize(file_path) # tamanho do arquivo em bytes
            number_of_parts = self.get_number_of_parts(file_size) # número de partes em que o arquivo será dividido

            # envia uma mensagem de confirmação para o peer, contendo a quantidade de partes em que o arquivo será dividido
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

            # espera a confirmação do peer para iniciar o envio das partes do arquivo
            req = client_socket.recv(1024).decode()
            req = json.loads(req)

            # se confirmado, começa a enviar as partes do arquivo
            if req["message"] == "DOWNLOAD_READY":
                self.upload(file_path, number_of_parts, client_socket)
    
    # função que realiza o join do peer no servidor (JOIN)
    def join(self, server_host, server_port):
        self.create_socket()
        self.socket.connect((server_host, server_port))

        # mensagem da requisição
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

        # se o join foi realizado com sucesso, imprime uma mensagem de sucesso
        if res["message"] == "JOIN_OK":
            print("\nSou peer {}:{} com arquivos {}"
                  .format(self.host, self.port, self.get_file_names(self.files))
            )

        self.socket.close()

    # função que realiza o update do peer no servidor (UPDATE)
    def update(self, file: str, server_host, server_port):
        self.create_socket()
        self.socket.connect((server_host, server_port))

        # mensagem da requisição, com o arquivo que será adicionado
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

    # função que realiza a busca de um arquivo no servidor (SEARCH)
    def search(self, file: str, server_host, server_port):
        self.create_socket()
        self.socket.connect((server_host, server_port))

        # mensagem da requisição, com o arquivo que será buscado
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

    # função que realiza o download de um arquivo de um peer (DOWNLOAD)
    def download(self, host: str, port: int, file_name: str):
        self.create_socket()
        self.socket.connect((host, port)) # conecta com o peer

        # mensagem da requisição, com o arquivo que será baixado
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

        # se o arquivo não existe mais no peer, encerra o processo de download
        if res["message"] == "FILE_NOT_FOUND":
            #print("\nArquivo não encontrado")
            return
        
        # arquivo encontrado, começa o processo de download

        # mensagem de confirmação para o peer
        req = json.dumps({
            "message": "DOWNLOAD_READY",
            "data": {
                "host": self.host,
                "port": self.port
            }
        })

        self.socket.send(req.encode())

        # caminho do arquivo que será baixado
        file_path = os.path.join(self.folder, file_name)

        # cria o arquivo que será baixado
        with open(file_path, "wb") as file:
            for i in range(res["data"]["number_of_parts"]):
                part = self.socket.recv(PART_SIZE) # recebe uma parte do arquivo
                file.write(part) # escreve a parte do arquivo no arquivo que está sendo baixado

                self.socket.send("Dados recebidos".encode()) # envia uma mensagem de confirmação para o peer

            print("\nArquivo {} baixado com sucesso na pasta {}".format(file_name, self.folder))

            # atualiza o servidor com o novo arquivo
            self.update(file_name, SERVER_HOST, SERVER_PORT)

    # função que realiza o upload de um arquivo para um peer
    def upload(self, file_path: str, number_of_parts: int, client_socket: socket.socket) -> None:
        with open(file_path, "rb") as file:
            for i in range(number_of_parts):
                part = file.read(PART_SIZE) # lê uma parte do arquivo
                client_socket.send(part) # envia a parte do arquivo para o peer
                msg = client_socket.recv(1024).decode() # espera a confirmação do peer

    # função que retorna o número de partes em que um arquivo será dividido
    def get_number_of_parts(self, file_size: int) -> int:
        return math.ceil(file_size / PART_SIZE)

    # função que verifica se um arquivo existe na pasta do peer
    def check_file_exists(self, file: str) -> bool:
        files = self.list_files()

        if file in files:
            return True
        
        return False

    # função que lista os arquivos da pasta do peer
    def list_files(self) -> list:
        scan = os.scandir(self.folder)
        file_names = []

        for record in scan:
            file_names.append(record.name)

        return list(dict.fromkeys(file_names))

    # função que retorna os nomes dos arquivos de uma lista de arquivos
    def get_file_names(self, files: list) -> str:
        file_names = ""

        for file in files:
            file_names += file + " "

        return file_names.strip()
    
    # função que retorna as informações dos peers de uma lista de peers
    def get_peers_info(self, peers: list) -> str:
        peers_info = ""

        for peer in peers:
            peers_info += "{}:{} ".format(peer[0], peer[1])

        return peers_info.strip()
    
    # função que cria um socket TCP
    def create_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == "__main__":

    peer = None
    peers = None
    file = None

    while True:

        # menu interativo para escolha da ação

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

            # cria o peer
            peer = Peer(host, port, folder)

            # realiza o join do peer no servidor
            peer.join(SERVER_HOST, SERVER_PORT)

        elif option == "2": # SEARCH
            print("Insira o nome do arquivo que deseja procurar (com extensão): ", end="")
            file = input()
            
            # realiza a busca do arquivo no servidor
            peer.search(file, SERVER_HOST, SERVER_PORT)

        elif option == "3": # DOWNLOAD
            print("Insira o IP do peer que possui o arquivo: ", end="")
            ip_peer = input()

            print("Insira a porta do peer que possui o arquivo: ", end="")
            port_peer = int(input())

            # realiza o download do arquivo
            peer.download(ip_peer, port_peer, file)
