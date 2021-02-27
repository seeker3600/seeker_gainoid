from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import tempfile
from os import path
from multiprocessing import Process, Barrier
import time


def simple_http_handler(directory):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    return Handler


def publish_a_file(dir, port) -> Process:

    barrier = Barrier(2)

    def func(dir, port, barrier):
        with TCPServer(("", port), simple_http_handler(dir)) as server:
            barrier.wait()
            server.handle_request()

    proc = Process(target=func, args=(dir, port, barrier))
    proc.start()
    barrier.wait()
    time.sleep(0.05)

    return proc


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as dname:

        with open(path.join(dname, "test.txt"), "wt") as f:
            f.write("yeah")

        proc = publish_a_file(dname, 8081)
        print("wait...")
        proc.join()
        print("close...")
