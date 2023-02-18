import zmq
import threading
from threading import Lock, Thread
import uuid
import json
from components.port import get_new_port
from time import sleep
cxt = zmq.Context()
mutex = threading.Lock()

class Client:
    def __init__(self):
        self.unique_id=str(uuid.uuid1())
        self.joined_servers={}
        self.sock_addr = "127.0.0.1"
        self.sock_port = get_new_port()

    def start(self):
        msg, status = self.__setup()

        if status:
            print(msg)
            self.terminal_lock=Lock()
            self.consumer_thread=Thread(target=self.__turn_up, args=[self.__handle_request])
            self.consumer_thread.start()
            """ while True:
                with mutex:
                    try:
                        request = self.__client_socket.recv()
                        self.__handle_request(request)
                    except zmq.Again:
                        print("No request") """

    def __setup(self):
        msg = "CONNECTED Successfully"
        status = False
        self.__registry_socket = cxt.socket(zmq.REQ)
        result = self.__registry_socket.connect("tcp://127.0.0.1:5556")
        if result:
            status = True
        else:
            msg = "FAILED on Connect()"
        return msg, status
    
    def __turn_up(self, on_request):
        self.__client_socket = cxt.socket(zmq.REP)
        self.__client_socket.setsockopt(zmq.SNDTIMEO, 1000)
        self.__client_socket.setsockopt(zmq.RCVTIMEO, 1000)
        addr = "tcp://{0}:{1}".format(self.sock_addr, self.sock_port)
        result = self.__client_socket.bind(addr)

        with mutex:
            try:
                req = self.__client_socket.recv()
                on_request(req)
            except zmq.Again:
                sleep(0.2)
            finally:
                sleep(0.2)
    
    def __handle_request(self, req):
        args = req.decode()
        request=json.loads(args)
        print(request)

        """ if (request['request_type']=='get_server_list'):
            self.print_server_list(request['response'])
        elif (request['request_type']=='join_server'):
            self.join_server_success(request['response'])
        elif (request['request_type']=='leave_server'):
            self.leave_server_success(request['response'])
        elif (request['request_type']=='publish_article'):
            self.publish_article_success(request['response'])
        elif (request['request_type']=='get_article'):
            self.get_article_success(request['response']) 
        """
    def join_server(self):
        pass

    def leave_server(self):
        pass

    def publish_service(self):
        pass
    def get_article(self):
        pass

    def __print_server_list(self, server_list):
        print('----------------\nLIST OF AVAILABLE SERVERS')
        for server_name in server_list.keys():
            print(f'{server_name} {server_list[server_name]}')
    
    def get_server_list(self):
        request={
            'request_type':'get_server_list',
            'arguments': {
                'address': self.unique_id
            }
        }
        self.__registry_socket.send_string(json.dumps(request))
        raw_response = self.__registry_socket.recv()
        
        response = json.loads(raw_response.decode())
        
        self.__print_server_list(response["response"])

    def print_server(self):
        pass
