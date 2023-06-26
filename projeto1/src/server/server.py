import json
import socket

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        # dicionário que armazena os arquivos e os peers que os possuem, na seguinte estrutura:
        # { ( file_name , [ (host , port) , ... ] ) , ... }
        self.files_peers = dict()

        # cria um socket TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    # função que fica escutando por novas conexões de peers
    def run(self):
        try:
            self.socket.listen(5)

            while True:
                client_socket, address = self.socket.accept()

                req = client_socket.recv(1024).decode()

                res = self.handle_request(req)

                client_socket.send(res.encode())

                client_socket.close()
        
        finally:
            self.socket.close()

    # função que direciona a requisição para a função correta de acordo com a ação
    def handle_request(self, req: str) -> str:
        res = None
        req = json.loads(req)

        if req["action"] == "JOIN":
            res = self.handle_join(req["data"])
        elif req["action"] == "SEARCH":
            res = self.handle_search(req["data"])
        elif req["action"] == "UPDATE":
            res = self.handle_update(req["data"])

        return json.dumps(res)
        
    # função que adiciona um novo peer e seus arquivos ao servidor (JOIN)
    def handle_join(self, data: dict) -> dict:
        files = data["files"]

        for file in files:
            self.create_file(file)
            self.insert_peer(data["host"], data["port"], file)

        print("Peer {}:{} adicionado com arquivos {}"
              .format(data["host"], data["port"], self.get_file_names(files))
        )

        return {"message": "JOIN_OK"}

    # função que retorna os peers que possuem o arquivo solicitado (SEARCH)
    def handle_search(self, data: dict) -> dict:
        file = data["file"]
        host = data["host"]
        port = data["port"]

        print("Peer {}:{} solicitou arquivo {}".format(host, port, file))

        if file in self.files_peers:
            return {"message": "SEARCH_OK", "data": {"peers": self.files_peers[file]}}

        return {"message": "SEARCH_OK", "data": {"peers": []}}

    # função que adiciona um novo arquivo a um peer (UPDATE)
    def handle_update(self, data: dict) -> dict:
        file = data["file"]
        host = data["host"]
        port = data["port"]
    
        self.create_file(file)
        self.insert_peer(host, port, file)

        return {"message": "UPDATE_OK"}

    # função que cria um registro de um novo arquivo, caso ele não exista
    def create_file(self, file: str) -> None:
        if file not in self.files_peers:
            self.files_peers[file] = []

    # função que insere um peer em um arquivo, caso ele não esteja inserido
    def insert_peer(self, host, port, file) -> None:
        peer = (host, port)

        if peer not in self.files_peers[file]:
            self.files_peers[file].append(peer)

    # função que retorna uma string com os nomes dos arquivos
    def get_file_names(self, files: list) -> str:
        file_names = ""

        for file in files:
            file_names += file + " "

        return file_names.strip()

if __name__ == "__main__":
    print("Insira o endereco IP do servidor: ", end="")
    host = input()
    print("Insira a porta do servidor: ", end="")
    port = int(input())

    # cria o servidor e o executa
    server = Server(host, port)
    server.run()
