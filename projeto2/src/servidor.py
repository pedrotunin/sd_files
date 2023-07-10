import socket

from mensagem import Mensagem

class Servidor:
    def __init__(self, ip: str, port: int, ip_leader: str, port_leader: int) -> None:
        self.ip = ip
        self.port = port
        self.ip_leader = ip_leader
        self.port_leader = port_leader
        self.is_leader = self.determine_leader()

    def start(self) -> None:
        pass

    # determina se o servidor é o líder
    def determine_leader(self) -> bool:
        return (self.ip, self.port) == (self.ip_leader, self.port_leader)
    

if __name__ == "__main__":
    print("Insira o IP do servidor: ", end="")
    ip = input()
    print("Insira a porta do servidor: ", end="")
    port = int(input())

    print("Insira o IP do líder: ", end="")
    ip_leader = input()
    print("Insira a porta do líder: ", end="")
    port_leader = int(input())

    servidor = Servidor(ip, port, ip_leader, port_leader)
    servidor.start()