import logging
import asyncio

import zmq
import zmq.asyncio

from utils import ainput

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.INFO
)


class P2PClient:

    def __init__(self, name, port, ip, is_server):
        """
        :param port: is_server determines if this port is binded or used for connection
        """
        self.name = name
        self.socket = zmq.asyncio.Context().socket(zmq.PAIR)

        if is_server:
            self.socket.bind(f'tcp://*:{port}')
            logging.info('Socket binded.')
        else:
            self.socket.connect(f'tcp://{ip}:{port}')
            logging.info('Connection ready.')

    async def run_sender(self):
        while True:
            text = await ainput('')
            await self.socket.send_json(
                {
                    'name': self.name,
                    'text': text
                }
            )

    async def run_receiver(self):
        while True:
            data = await self.socket.recv_json()
            print(f'[{data["name"]}] {data["text"]}', end='')

    def start(self, loop):
        loop.create_task(self.run_receiver())
        loop.create_task(self.run_sender())

    async def disconnect(self):
        await self.socket.send_json(
            {
                'name': self.name,
                'text': 'I\'m off.'
            }
        )

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--name', help='Client name')
    parser.add_argument('--port', type=int, help='Port of this client/server')
    parser.add_argument('--ip', help='IP of server. Use \'all\' for *')
    parser.add_argument('--server', action='store_true', help='If present this will be a server')

    args = parser.parse_args()
    args.ip = '*' if args.ip == 'all' else args.ip

    clt = P2PClient(
        name=args.name,
        port=args.port,
        ip=args.ip,
        is_server=args.server
    )

    try:
        loop = asyncio.get_event_loop()
        clt.start(loop)
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info('Stopped by user!')
