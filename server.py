#!/usr/bin/env python3

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

# Configura a entrada de novos clientes.
def accept_incoming_connections():
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s conectou-se." % client_address)
        client.send(bytes("Bem-vindo ao chat!", "utf8"))
        client.send(bytes("Digite o seu o nome!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


# Configura a conexão do cliente.
def handle_client(client):
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Bem-vindo %s! Caso queira sair, digite {quit}.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s entrou no chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        if msg != bytes("{quit}", "utf8"):
            broadcast(msg, name+": ")
        else:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            broadcast(bytes("%s saiu do chat." % name, "utf8"))
            break


# Transmite a mensagem para todos os clientes.
def broadcast(msg, prefix=""):
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)

# def private_broadcast(msg, prefix="", )

       
clients = {}
addresses = {}

HOST = "localhost"
PORT = 33000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Aguardando conexão...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()