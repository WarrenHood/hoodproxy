import socket
import logging
import time
from threading import Thread
from dataclasses import dataclass


@dataclass
class IPV4Address:
    ip: str
    port: int

    def __repr__(self) -> str:
        return f"{self.ip}:{self.port}"

    def listen_tcp(self, listen_backlog=100) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, self.port))
        sock.listen(listen_backlog)
        return sock


@dataclass
class IPV4Target:
    address: IPV4Address

    def connect_tcp(self) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.address.ip, self.address.port))
        return sock


class TCPProxy:
    listen_addr: IPV4Address
    listener: socket.socket
    listen_thread: Thread
    dest_addr: IPV4Target
    dest_socket: socket.socket
    proxy_threads: list[Thread]
    should_stop: bool

    def __init__(self, listen_addr: IPV4Address, dest: IPV4Target) -> None:
        self.should_stop = False
        self.listen_addr = listen_addr
        self.dest_addr = dest

    def run(self) -> None:
        if self.should_stop:
            raise Exception("Cannot start proxy while it is already running")
        logging.info(f"Starting proxy ({self.listen_addr} -> {self.dest_addr})")
        self.should_stop = False
        self.listener = self.listen_addr.listen_tcp()
        self.proxy_threads = []
        self.listen_thread = Thread(target=self.accept_connections)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def stop(self) -> None:
        if self.should_stop:
            raise Exception("Cannot stop already stopped proxy")
        logging.info(f"Stopping TCP proxy ({self.listen_addr} -> {self.dest_addr})")
        self.should_stop = True
        for t in self.proxy_threads:
            t.join()
        self.proxy_threads = []

    def accept_connections(self):
        while not self.should_stop:
            try:
                client, addr = self.listener.accept()
                logging.info(f"Got new connection at {addr}. Proxying traffic...")
                server_sock = self.dest_addr.connect_tcp()

                t1 = Thread(target=self.forward_traffic, args=(addr, client, self.dest_addr, server_sock))
                t2 = Thread(target=self.forward_traffic, args=(self.dest_addr, server_sock, addr, client))
                self.proxy_threads += [t1, t2]
                t1.start()
                t2.start()
            except Exception:
                logging.exception("Error while attempting to proxy a new connection")
                time.sleep(.5)


    def forward_traffic(
        self, src_addr: IPV4Address, src_socket: socket.socket, dest_addr: IPV4Address, dest_socket: socket.socket
    ) -> None:
        logging.info(f"[{src_addr} -> {dest_addr}] Ready to forward packets...")
        while not self.should_stop:
            msg = src_socket.recv(1024)
            if len(msg) > 0:
                print(f"[{src_addr} -> {dest_addr}]\nBytes:\n{msg}\nDecoded:\n{msg.decode(errors='ignore')}")
            dest_socket.send(msg)
