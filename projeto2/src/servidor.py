import socket
import threading
import concurrent.futures
from datetime import datetime

from mensagem import Mensagem

class Servidor:
    def __init__(self, ip: str, port: int, ip_leader: str, port_leader: int) -> None:
        self.ip = ip
        self.port = port
        self.ip_leader = ip_leader
        self.port_leader = port_leader
        self.is_leader = self.determine_leader()
        self.servers = [("127.0.0.1", 10097), ("127.0.0.1", 10098), ("127.0.0.1", 10099)]

        self.keys = dict() # keys: [key:{value, timestamp}]

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.ip, self.port))

        self._lock = threading.Lock()

    def start(self) -> None:
        try:
            self.socket.listen(5)

            while True:
                client_socket, address = self.socket.accept()

                req = client_socket.recv(1024).decode()

                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    executor.map(self.handle_request, [req], [client_socket])

        finally:
            self.socket.close()

    def handle_request(self, req: str, client_socket: socket.socket) -> None:
        mensagem_res = None
        mensagem_req = Mensagem.from_json(req)

        if mensagem_req.type == "PUT":
            mensagem_res = self.handle_put(mensagem_req.content["data"], client_socket)
        elif mensagem_req.type == "GET":
            mensagem_res = self.handle_get(mensagem_req.content["data"], client_socket)
        elif mensagem_req.type == "REPLICATION":
            mensagem_res = self.handle_replication(mensagem_req.content["data"])

        client_socket.send(mensagem_res.to_json().encode())
        client_socket.close()
    
    def handle_put(self, data: dict, client_socket: socket.socket) -> Mensagem:
        now = self.now()
        key = data["key"]
        value = data["value"]

        if not self.is_leader:
            print("\nEncaminhando PUT key:{} value:{}".format(key, value))
            return Mensagem("PUT_FOWARD", {"data": {"ip_leader": self.ip_leader, "port_leader": self.port_leader}})

        client_ip, client_port = client_socket.getpeername()

        print("\nCliente {}:{} PUT key:{} value:{}".format(client_ip, client_port, key, value))

        self.update_key(key, value, now)

        replication_count = 0
        other_servers = self.get_other_servers()
        
        for server in other_servers:
            mensagem = Mensagem("REPLICATION", {"data": {"key": key, "value": value, "timestamp": now}})
            response = self.replicate(server, mensagem)
            if response.type == "REPLICATION_OK":
                replication_count += 1

        if replication_count == len(other_servers):
            print("\nEnviando PUT_OK ao Cliente {}:{} da key:{} ts:{}".format(client_ip, client_port, key, now))
            return Mensagem("PUT_OK", {"data": {"timestamp": now}})

    def handle_get(self, data: dict, client_socket: socket.socket) -> Mensagem:
        key = data["key"]
        client_ip, client_port = client_socket.getpeername()

        if key not in self.keys:
            print("\nCliente {}:{} GET key:{} ts:{}. Meu ts é {}, portanto devolvendo {}".format(
                client_ip, client_port, key, data["timestamp"], 0, "NULL"
            ))
            return Mensagem("GET_RESPONSE", {"data": {"value": "NULL", "timestamp": data["timestamp"]}})
        
        if self.keys[key]["timestamp"] < data["timestamp"]:
            print("\nCliente {}:{} GET key:{} ts:{}. Meu ts é {}, portanto devolvendo {}".format(
                client_ip, client_port, key, data["timestamp"], self.keys[key]["timestamp"], "TRY_OTHER_SERVER_OR_LATER"
            ))
            return Mensagem("GET_RESPONSE", {"data": {"value": "TRY_OTHER_SERVER_OR_LATER", "timestamp": data["timestamp"]}})
        
        print("\nCliente {}:{} GET key:{} ts:{}. Meu ts é {}, portanto devolvendo {}".format(
            client_ip, client_port, key, data["timestamp"], self.keys[key]["timestamp"], self.keys[key]["value"]
        ))
        return Mensagem("GET_RESPONSE", {"data": {"value": self.keys[key]["value"], "timestamp": self.keys[key]["timestamp"]}})

    def handle_replication(self, data: dict) -> Mensagem:
        key = data["key"]
        value = data["value"]
        timestamp = data["timestamp"]

        print("\nREPLICATION key:{} value:{} ts:{}".format(key, value, timestamp))

        self.update_key(key, value, timestamp)

        return Mensagem("REPLICATION_OK", {"data": {"timestamp": timestamp}})

    def replicate(self, server: tuple, mensagem: Mensagem) -> Mensagem:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(server)

        mensagem = mensagem.to_json()
        s.send(mensagem.encode())
        res = s.recv(1024).decode()

        s.close()

        return Mensagem.from_json(res)

    # retorna os outros servidores
    def get_other_servers(self) -> list:
        other_servers = []
        for server in self.servers:
            if server != (self.ip, self.port):
                other_servers.append(server)
        return other_servers

    # atualiza uma key
    def update_key(self, key: str, value: str, timestamp: int) -> None:
        with self._lock:
            self.keys[key] = {
                "value": value,
                "timestamp": timestamp
            }

    # retorna o timestamp atual
    def now(self) -> int:
        return int(datetime.now().timestamp())

    # determina se o servidor é o líder
    def determine_leader(self) -> bool:
        return (self.ip, self.port) == (self.ip_leader, self.port_leader)
    
if __name__ == "__main__":
    print("Insira o IP do servidor: ", end="")
    ip = "127.0.0.1"#input()
    print("Insira a porta do servidor: ", end="")
    port = int(input())

    print("Insira o IP do líder: ", end="")
    ip_leader = "127.0.0.1"#input()
    print("Insira a porta do líder: ", end="")
    port_leader = 10097#int(input())

    servidor = Servidor(ip, port, ip_leader, port_leader)
    servidor.start()