import socket

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        print("Servidor rodando em {}:{}".format(self.host, self.port))

        self.socket.bind((self.host, self.port))
        self.socket.listen(5)

        while True:
            client_socket, address = self.socket.accept()
            pass

if __name__ == "__main__":

    print("Insira o endereco IP do servidor: ")
    host = input()
    print("Insira a porta do servidor: ")
    port = int(input())

    server = Server(host, port)
    server.run()
