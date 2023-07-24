import socket
import random

from mensagem import Mensagem

INIT = "1"
PUT = "2"
GET = "3"

class Cliente:
    def __init__(self, servers: list) -> None:
        self.servers = servers # lista dos servidores (ip, port)
        self.timestamps = dict() # timestamps das keys: [(key, timestamp)]
        self.socket = None # socket TCP

    # Envia uma mensagem PUT para um servidor
    def put(self, key: str, value: str) -> None:
        server = self.choose_server()

        data = {
            "key": key,
            "value": value
        }
        mensagem = Mensagem("PUT", {"data": data})
        mensagem_res = self.send_request(server, mensagem)
        data = mensagem_res.content["data"]
        
        # Em caso de PUT_OK, atualiza o timestamp da key (o servidor escolhido foi o líder)
        if mensagem_res.type == "PUT_OK":
            print("\nPUT_OK key: {} value {} timestamp {} realizada no servidor {}:{}".format(
                key, value, data["timestamp"], server[0], server[1]
            ))
            self.set_timestamp(key, data["timestamp"])

        # Em caso de PUT_FOWARD, encaminha a mensagem para o líder
        elif mensagem_res.type == "PUT_FOWARD":
            leader = (data["ip_leader"], data["port_leader"])

            mensagem_res = self.send_request(leader, mensagem)
            data = mensagem_res.content["data"]

            if mensagem_res.type == "PUT_OK":
                print("\nPUT_OK key: {} value {} timestamp {} realizada no servidor {}:{}".format(
                    key, value, data["timestamp"], server[0], server[1]
                ))
                self.set_timestamp(key, data["timestamp"])

    # Envia uma mensagem GET para um servidor
    def get(self, key: str) -> None:
        server = self.choose_server()

        data = {
            "key": key,
            "timestamp": self.get_timestamp(key)
        }
        mensagem = Mensagem("GET", {"data": data})
        mensagem_res = self.send_request(server, mensagem)
        data = mensagem_res.content["data"]

        # Ao receber o GET_RESPONSE, imprime o valor da key
        if mensagem_res.type == "GET_RESPONSE":
            print("\nGET key: {} value: {} obtido do servidor {}:{}, meu timestamp {} e do servidor {}".format(
                key, data["value"], server[0], server[1], self.get_timestamp(key), data["timestamp"]
            ))

            # atualiza o timestamp da key se o valor não for TRY_OTHER_SERVER_OR_LATER
            if data["value"] != "NULL" and data["value"] != "TRY_OTHER_SERVER_OR_LATER":
                self.set_timestamp(key, data["timestamp"])

    # Envia uma mensagem para um servidor e retorna a resposta
    def send_request(self, server: tuple, mensagem: Mensagem) -> Mensagem:
        self.create_socket()
        self.socket.connect(server)

        mensagem = mensagem.to_json()
        self.socket.send(mensagem.encode())
        res = self.socket.recv(1024).decode()

        self.socket.close()

        return Mensagem.from_json(res)

    # retorna o timestamp da key
    def get_timestamp(self, key: str) -> int:
        if key in self.timestamps:
            return self.timestamps[key]
        return 0
    
    # atualiza o timestamp da key
    def set_timestamp(self, key: str, timestamp: int) -> None:
        self.timestamps[key] = timestamp

    # escolhe um servidor aleatório
    def choose_server(self) -> tuple:
        return random.choice(self.servers)

    # função que cria um socket TCP
    def create_socket(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == "__main__":
    cliente = None

    while True:
        print("\nInsira a opção da ação que deseja realizar (1, 2 ou 3): ")
        print("1 - INIT")
        print("2 - PUT")
        print("3 - GET")

        option = input("Opção: ")

        while option not in ["1", "2", "3"]:
            print("Opção inválida. Tente novamente.")
            option = input("Opção: ")

        # Inicialização do cliente
        if option == INIT:
            servers = list()

            for i in range(1, 4):
                print(f"Digite o IP do servidor {i}: ", end="")
                ip = input()
                print(f"Digite a porta do servidor {i}: ", end="")
                port = int(input())
                servers.append((ip, port))

            cliente = Cliente(servers)

        # Obtém key e value e envia uma mensagem PUT 
        elif option == PUT:
            print("Digite a key: ", end="")
            key = input()
            print("Digite o value: ", end="")
            value = input()

            cliente.put(key, value)

        # Obtém key e envia uma mensagem GET
        elif option == GET:
            print("Digite a key: ", end="")
            key = input()

            cliente.get(key)
