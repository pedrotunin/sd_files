import socket
import random

from mensagem import Mensagem

class Cliente:
    def __init__(self, servers: list) -> None:
        self.servers = servers

    # escolhe um servidor aleatório
    def choose_server(self) -> tuple:
        return random.choice(self.servers)

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

        if option == "1": # INIT
            servers = list()
            # As portas default dos servidores são 10097, 10098 e 10099

            for i in range(1, 4):
                print(f"Digite o IP do servidor {i}: ", end="")
                ip = input()
                print(f"Digite a porta do servidor {i}: ", end="")
                port = int(input())
                servers.append((ip, port))

            cliente = Cliente(servers)
    
        elif option == "2": # PUT
            print("Digite a key: ", end="")
            key = input()
            print("Digite o value: ", end="")
            value = input()



        elif option == "3": # GET
            pass
