import zmq
import threading
import uuid
import json
from components.port import get_new_port

cxt = zmq.Context()
mutex = threading.Lock()

class Client:
    def __init__(self):
        pass

    def start(self):
        pass

    def setup(self):
        pass

    def handle_request(self):
        pass

    def join_server(self):
        pass

    def leave_server(self):
        pass

    def publish_service(self):
        pass
    def get_article(self):
        pass

    def get_server_list(self):
        pass
    
    def print_server(self):
        pass
