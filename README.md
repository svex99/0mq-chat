# 0mq-chat

## Requerimientos:
    
    pyzmq==22.03

## Chat Peer to Peer

Establece una conexion entre dos socket de tipo PAIR y maneja todo el intercambio de datos por dichos puntos. El intercambio es asincrono.

    usage: p2p.py [-h] [--name NAME] [--port PORT] [--ip IP] [--server]

    optional arguments:
    -h, --help   show this help message and exit
    --name NAME  Client name
    --port PORT  Port of this client/server
    --ip IP      IP of remote server
    --server     If present this will be a server (--ip will be ignored)

Ejemplo cliente esperando conexion:

    python3 p2p.py --name client1 --port 8888 --ip * --server

Ejemplo de cliente que se conecta a otro cliente (client1, asumiendo q esten en el mismo sistema):

    python3 p2p.py --name client2 --port 8888 --ip localhost

## Chat Room

Crea un servidor (ROUTER) que acepta multiples conexiones desde diferentes clientes (DEALER).

Funcionalidades:

- La comunicacion entre cada cliente y el servidor se asincrona.
- Cada mensaje que llega de un cliente al servidor es enviado a los demas clientes.
- Los clientes son notificados cuando otro entra/sale del chat. 

### Servidor

    usage: server.py [-h] [--port PORT] [--ip IP] [--name NAME]

    optional arguments:
    -h, --help   show this help message and exit
    --port PORT  Server port
    --ip IP      Server IP
    --name NAME  Server name

Ejemplo de uso:

    python3 --port 9999 --ip * --name chatroom-server

### Cliente

    usage: client.py [-h] [--port PORT] [--ip IP] [--name NAME]

    optional arguments:
    -h, --help   show this help message and exit
    --port PORT  Server port
    --ip IP      Server IP
    --name NAME  Client name

Ejemplo de uso:

    python3 client.py --port 9999 --ip localhost --name "John Doe"

