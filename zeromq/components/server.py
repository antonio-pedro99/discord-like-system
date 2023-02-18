import zmq
import threading
import uuid
import json
from port import get_new_port

cxt = zmq.Context()
mutex = threading.Lock()
class Server:
    def __init__(self):
        self.server_queue_name=str(uuid.uuid1())
        self.MAXCLIENTS=10
        self.CLIENTELE=[]
        self.current_clients=0
        self.sock_addr = "127.0.0.1"
        self.sock_port = get_new_port()
        self.article_list=[]

    def  start(self):
        msg, status = self.__setup()

        if status:
            print(msg)
            reg_status = self.__register()
            if reg_status:
                print("STARTING CLIENT at", self.sock_port)
                self.__turn_up()
                while True:
                    with mutex:
                        try:
                            request = self.__server_socket.recv()
                            self.__handle_request(request)
                        except zmq.Again:
                            print("No request")

        else:
            print(msg)

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
    
    def __turn_up(self):
        self.__server_socket = cxt.socket(zmq.REP)
        self.__server_socket.setsockopt(zmq.SNDTIMEO, 1000)
        self.__server_socket.setsockopt(zmq.RCVTIMEO, 1000)
        addr = "tcp://{0}:{1}".format(self.sock_addr, self.sock_port)
        result = self.__server_socket.bind(addr)
        
        #print("LISTEN at", addr)

    def __handle_request(self, req):
        args = req.decode()
        request=json.loads(args)
        if (request['request_type']=='register'):
            print('REGISTER REQUEST: ',request['response'])
        elif (request['request_type']=='join_server'):
            self.join_server(request['arguments']['unique_id'])
        elif (request['request_type']=='leave_server'):
            self.leave_server(request['arguments']['unique_id'])
        elif (request['request_type']=='publish_article'):
            self.publish_article(request['arguments'])
        """ elif (request['request_type']=='get_article'):
            self.get_article(request['arguments']) """

    def get_article(self):
        pass

    def publish_article(self, args):
       pass


    def leave_server(self, client_uuid):
        print(f'LEAVE REQUEST FROM {client_uuid}')
        status='FAIL'
        try:
            status='SUCCESS'
            if(client_uuid in self.CLIENTELE):
                self.CLIENTELE.remove(client_uuid)
                self.current_clients-=1
        except:
            pass
        response = json.dumps({'request_type':'leave_server', 'response':status})
        self.__server_socket.send_string(response)

    def join_server(self, client_uuid):
        print(f'JOIN REQUEST FROM {client_uuid}')
        status='FAIL'
        try:
            if (client_uuid in self.CLIENTELE):
                status='SUCCESS'
            else:
                if (self.current_clients<self.MAXCLIENTS):
                    status='SUCCESS'
                    self.CLIENTELE.append(client_uuid)
                    self.current_clients+=1
        except:
            pass
        response =json.dumps({'request_type':'join_server', 'response':status})
        self.__server_socket.send_string(response)

    def __register(self)->bool:
        self.server_name =input("INPUT NAME OF THE SERVER: ")
        addr = "{0}:{1}".format(self.sock_addr, self.sock_port)
        request = {
            'request_type':'register',
            'arguments': {
                'name': self.server_name,
                'address': addr,
                'status': 'up'
            }
        }

        self.__registry_socket.send_string(json.dumps(request))
        
        raw_response = self.__registry_socket.recv()
        
        response = json.loads(raw_response.decode())  
        return response["response"] == "SUCCESS"

server = Server()
server.start()