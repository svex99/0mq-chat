import logging

import zmq


logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.INFO
)


class Server:

    def __init__(self, name, port, ip):
        self.name = name
        self.addr = (ip, port)
        self.socket = zmq.Context().socket(zmq.ROUTER)
        self.clients = []

    def start(self):
        self.socket.bind(f'tcp://*:{self.addr[1]}')
        logging.info(f'[{self.name}] binded to {self.addr}')

        while True:
            client_id = self.socket.recv()
            data = {k: v for k, v in self.socket.recv_json().items()}
            logging.info(f'Data received from [{client_id}] {data}')

            if 'auth' in data or client_id not in self.clients:
                if data['auth'] or client_id not in self.clients:
                    self.clients.append(client_id)
                elif not data['auth']:
                    try:
                        self.clients.remove(client_id)
                    except ValueError:
                        logging.warning('Disconnected client of previous session.')
                        pass

                msg = f'{data["name"]} {"joined" if data["auth"] else "left"} the room. ' \
                    f'{len(self.clients)} online.'

                data.pop('auth')
                data = {
                    'name': self.name,
                    'text': msg + '\n'
                }

                logging.info(msg)

            count = 0
            for client in self.clients:
                if client != client_id:
                    self.socket.send(client, zmq.SNDMORE)
                    self.socket.send_json(data)
                    count += 1
            logging.info(f'Delivered data from [{client_id}] to {count} clients.')


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--port', type=int, help='Server port')
    parser.add_argument('--ip', default='*', help='Server IP')
    parser.add_argument('--name', type=str, default='server', help='Server name')
    args = parser.parse_args()

    server = Server(
        name=args.name,
        port=args.port,
        ip=args.ip
    )

    try:
        server.start()
    except KeyboardInterrupt:
        logging.info('Server stopped by user!')
