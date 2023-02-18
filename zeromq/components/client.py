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
    

    def __send_request(self, server_address, request):
        socket = cxt.socket(zmq.REQ)
        conn = socket.connect("tcp://{0}".format(server_address))
        reply = None
        
        if conn:
            socket.send_string(request)
            reply = socket.recv()
        socket.disconnect("tcp://{0}".format(server_address))

        self.__handle_response(reply)
 
    def __handle_response(self, body):
        args = body.decode()
        request=json.loads(args)
        if (request['request_type']=='get_server_list'):
            self.print_server_list(request['response'])
        elif (request['request_type']=='join_server'):
            self.join_server_success(request['response'])
        elif (request['request_type']=='leave_server'):
            self.__leave_server_success(request['response'])
        elif (request['request_type']=='publish_article'):
            self.publish_article_success(request['response'])
        elif (request['request_type']=='get_article'):
            self.get_article_success(request['response'])

    def __print_server_list(self, server_list):
        print('----------------\nLIST OF AVAILABLE SERVERS')
        if len(server_list.keys()) != 0:
            for server_name in server_list.keys():
                print(f'{server_name} {server_list[server_name]}')
            self.choosen_server_name = input("Enter name to join: ")
            # join to the server
            if(self.choosen_server_name in server_list.keys()):
                self.joined_servers[self.choosen_server_name] = server_list[self.choosen_server_name]
                self.join_server(server_list[self.choosen_server_name])
            else:
                print('Entered Name Does not exist')
                #self.terminal_lock.acquire()
    
    def __leave_server_success(self,status):
        #self.terminal_lock.acquire()
        print(f"LEAVING REQUEST: {status}")
        if(status=='SUCCESS'):
            self.joined_servers.pop(self.choosen_server_name)
        #self.terminal_lock.release()

    def start(self):
        msg, status = self.__setup()

        if status:
            print(msg)
            self.terminal_lock= Lock()
            self.consumer_thread= Thread(target=self.__setup)
            self.consumer_thread.start()

    def join_server(self, server_address):
        request = {
            'request_type':'join_server',
            'arguments': {
                'unique_id': self.unique_id
            }
        }
        self.__send_request(server_address=server_address, request = json.dumps(request))
      

    def publish_service(self):
        pass
    
    def get_article(self):
        pass

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

    def leave_server(self):
        print("----------------\nJOINED SERVERS ARE:")
        for server_name in self.joined_servers.keys():
            print(server_name)
        self.choosen_server_name=input("Enter name to leave: ")
        if(self.choosen_server_name not in self.joined_servers.keys()):
            print("Entered Name Does not exist")
            return
        request={
            'request_type':'leave_server',
            'arguments': {
                'unique_id': self.unique_id
            }
        }
        server_address = self.joined_servers[server_name]
        self.__send_request(server_address = server_address, request =  json.dumps(request))
    
    def join_server_success(self, status):
        print(f"JOINING REQUEST: {status}")
        if(status=='FAIL'):
            self.joined_servers.pop(self.choosen_server_name)