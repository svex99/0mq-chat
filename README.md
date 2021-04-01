# 0mq-chat

## Requerimientos:
    
    pyzmq==22.03

## Chat Peer to Peer

Establece una conexion entre dos socket de tipo PAIR y maneja todo el intercambio de datos por dichos puntos. El intercambio es asincrono. Uno de los puntos debe hacer de servidor para recibir la conexion desde el otro extremo.

    usage: p2p.py [-h] [--name NAME] [--port PORT] [--ip IP] [--server]

    optional arguments:
    -h, --help   show this help message and exit
    --name NAME  Client name
    --port PORT  Port of this client/server
    --ip IP      IP of server. Use 'all' for *
    --server     If present this will be a server


Ejemplo cliente esperando conexion:

    python3 p2p.py --name client1 --port 8888 --ip all --server

Ejemplo de cliente que se conecta a otro cliente (client1, asumiendo q esten en el mismo sistema):

    python3 p2p.py --name client2 --port 8888 --ip localhost

## Chat Room

Crea un servidor (ROUTER) que acepta multiples conexiones desde diferentes clientes (DEALER).

Se escogio este acercamiento para minimizar el numero de sockets y de mensajes de un punto a otro, solo es necesario un socket en cada nodo (incluyendo servidor) para manejar todo el trafico que este recibe. Esto se logra al ser tanto ROUTER como DEALER bidireccionales, asincronos (no mantienen estados) y permitir multiples conexiones.

Funcionalidades:

- La comunicacion entre cada cliente y el servidor se asincrona.
- Cada mensaje que llega de un cliente al servidor es enviado a los demas clientes.
- Los clientes son notificados cuando otro entra/sale del chat. 
- Los clientes son notificados cuando el servidor se cierra (ctrl + C).
- Si el servidor se reinicia los clientes siguen mateniendo la conexion.

### Servidor

    usage: server.py [-h] [--port PORT] [--ip IP] [--name NAME]

    optional arguments:
    -h, --help   show this help message and exit
    --port PORT  Server port
    --ip IP      Server IP. Use 'all' for *
    --name NAME  Server name

Ejemplo de uso:

    python3 server.py --port 9999 --ip all --name chatroom-server

### Cliente

    usage: client.py [-h] [--port PORT] [--ip IP] [--name NAME]

    optional arguments:
    -h, --help   show this help message and exit
    --port PORT  Server port
    --ip IP      Server IP
    --name NAME  Client name

Ejemplo de uso:

    python3 client.py --port 9999 --ip localhost --name "John Doe"


### ¿Cómo hacer si un nodo se cae para que le lleguen todos los mensajes que se mandaron en ese momento?

En el ejemplo de chat cliente-servidor, el socket de tipo ROUTER que maneja el trafico en el servidor debe mantenerle la pista a cada conexion que el maneja, por tal motivo le asigna una identidad a cada conexion que recibe. Especificamente el socket servidor asigna un id n a la primera conexion que rcibe, a la siguiente n + 1, y asi de forma sucesiva.

Cuando el servidor se reinicia no es posible recuperar las conexiones anteriores a traves de los ids que tenian pues este vuelve a asignar los ids. Una alternativa es que el cliente intercambie con el servidor un identificador, asi el servidor puede almacenar las *updates* para cierto cliente hasta que este se conecte, con las credenciales correctas, para recibirlas.

### ¿Cómo hacer para que a todos los mensajes les lleguen en el mismo orden a todos?

En la implementacion adjunta de cliente-servidor el servidor no esta recibiendo y procesando la informacion de forma concurrente, es decir en cada iteracion recibe datos desde uno de los clientes, los procesa y envia la correspondiente informacion a los clientes. Dejando a un lado las demoras que puede causar la red, si un cliente envia informacion antes que cualquier otro, esta debe ser procesada y enviada a los demas clientes antes de que el servidor reciba nueva informacion.

### En el caso de que la red se particione, y se vuelve a reconectar, cómo manejar la consistencia y disponibilidad del sistema.

En la arquitectura actual si la red se particiona, los nodos que queden en la red a la que no tenga acceso el servidor quedaran aislados. Usando la idea planteada como respuesta a la primera interrogante una vez que la red se recupere todos los clientes desconectads pueden recibir la informcion que quedo pendiente de enviar hacia ellos. El problema en la idea anterior esta en que el grupo de clientes aislados del servidor quedaran incomunicados entre ellos a pesar de estar en la misma red, solucionar este problema traeria consigo la necesidad de que cada cliente fuera capaz de enviar la informacion directo a otro, en tal caso la arquitectura cliente-servidor no es apropiada.

Una alternativa podria ser que cada cliente tuviera un socket de tipo ROUTER para manejar la recepcion y otro de tipo DEALER para el envio. Todos los clientes deberian aceptar conexiones de todos los que tengan disponilbe en su red, asi como conectarse a ellos. Asi podrian enviar los mensajes a los restates en caso de que uno falte. 