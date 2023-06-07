import json
import socket

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        # { ( file_name , [ (host , port) , ... ] ) , ... }
        self.files_peers = dict()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

    def run(self):
        self.socket.listen(5)

        while True:
            client_socket, address = self.socket.accept()

            req = client_socket.recv(1024).decode()

            res = self.handle_request(req, address)

            client_socket.send(res.encode())

            client_socket.close()

    def handle_request(self, req: str, address) -> str:
        res = None
        req = json.loads(req)

        if req["action"] == "JOIN":
            res = self.handle_join(req["data"])
        elif req["action"] == "SEARCH":
            res = self.handle_search(req["data"], address)

        return json.dumps(res)
        
    def handle_join(self, data: dict) -> dict:
        files = data["files"]

        for file in files:
            if file not in self.files_peers:
                self.files_peers[file] = []

            peer = (data["host"], data["port"])

            if peer not in self.files_peers[file]:
                self.files_peers[file].append(peer)

        print("Peer {}:{} adicionado com arquivos {}"
              .format(data["host"], data["port"], self.get_file_names(files))
        )

        return {"message": "JOIN_OK"}

    def handle_search(self, data: dict, address) -> dict:
        file = data["file"]
        host, port = address

        print("Peer {}:{} solicitou arquivo {}".format(host, port, file))

        if file in self.files_peers:
            return {"message": "SEARCH_OK", "data": {"peers": self.files_peers[file]}}

        return {"message": "SEARCH_OK", "data": {"peers": []}}

    def get_file_names(self, files: list) -> str:
        file_names = ""

        for file in files:
            file_names += file + " "

        return file_names.strip()

if __name__ == "__main__":
    print("Insira o endereco IP do servidor: ")
    host = "127.0.0.1" #input()
    print("Insira a porta do servidor: ")
    port = 1099 #int(input())

    server = Server(host, port)
    server.run()
