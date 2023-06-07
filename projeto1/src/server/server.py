import socket

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        print("Servidor rodando em {}:{}".format(self.host, self.port))

        self.socket.bind((self.host, self.port))
        print("Socket binded to port {}".format(self.port))

        self.socket.listen(5)
        print("Socket is listening")

        while True:
            client_socket, address = self.socket.accept()
            print("Got a connection from {}".format(str(address)))
            
            #TODO: implementar lógica de comunicação com o cliente

            client_socket.close()

if __name__ == "__main__":

    print("Insira o endereco IP do servidor: ")
    host = "127.0.0.1" #input()
    print("Insira a porta do servidor: ")
    port = 1099 #int(input())

    server = Server(host, port)
    server.run()
