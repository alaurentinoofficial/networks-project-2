from socket import socket, AF_INET, SOCK_DGRAM

sock = socket(AF_INET, SOCK_DGRAM)

while True:
    mensagem = input()
    sock.sendto(mensagem.encode(), ('localhost', 8081))

    data, client_conn = sock.recvfrom(2048)

    print(data)

sock.close()
