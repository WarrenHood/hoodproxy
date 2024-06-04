import argparse
import logging
import time

from .types import IPV4Address, IPV4Target, TCPProxy


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="A TCP/UDP proxy")
    parser.add_argument("--listen-ip", type=str, default="0.0.0.0", help="Listen IP Address")
    parser.add_argument("--listen-port", type=int, required=True, help="Listen Port")
    parser.add_argument("--dest-ip", type=str, required=True, help="Destination IP Address")
    parser.add_argument("--dest-port", type=int, required=True, help="Destination Port")
    args = parser.parse_args()

    proxy = TCPProxy(
        IPV4Address(args.listen_ip, args.listen_port),
        IPV4Target(IPV4Address(args.dest_ip, args.dest_port))
    )
    proxy.run()
    while True:
        try:
            time.sleep(5)
        except Exception:
            proxy.stop()
            logging.exception("Exiting...")
            break
