#code for client
import pika
import json
import uuid
from time import sleep
from threading import Thread, Lock

class client:

    # all the connection initialisation for RabbitMQ
    def __init__(self):
        # all the important namings
        self.exchange_name='discord'
        self.registry_queue_name='registry_request'
        self.broker_ip='192.168.139.139'    # default port in use for registry
        self.unique_id=str(uuid.uuid1())
        self.joined_servers={}


    def start(self):
        # basic configuratons for RabbitMQ
        connection=pika.BlockingConnection(pika.ConnectionParameters(self.broker_ip))
        self.channel=connection.channel()
        self.channel.exchange_declare(
            exchange=self.exchange_name, 
            durable=True,
            exchange_type='direct'
        )
        self.terminal_lock=Lock()
        self.consumer_thread=Thread(target=self.setup_client_queue)
        self.consumer_thread.start()
        self.show_menu()


    def setup_client_queue(self):
        # this queue id for handling requests comming in register-server 
        client_queue=self.channel.queue_declare(
            queue=self.unique_id,
            durable=True
        )
        self.channel.queue_bind(
            exchange=self.exchange_name, 
            queue=client_queue.method.queue,
            routing_key=self.unique_id
        )
        self.channel.basic_consume(
            queue=client_queue.method.queue, 
            auto_ack=True, 
            on_message_callback=self.handle_request
        )
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()

    def handle_request(self, ch, method, properties, body):
        request=json.loads(body)
        if (request['request_type']=='get_server_list'):
            self.print_server_list(request['response'])
        elif (request['request_type']=='join_server'):
            self.join_server_success(request['response'])
        elif (request['request_type']=='leave_server'):
            self.leave_server_success(request['response'])


    def print_server_list(self, server_list):
        self.terminal_lock.acquire()
        print('----------------\nLIST OF AVAILABLE SERVERS')
        for server_name in server_list.keys():
             print(f'{server_name} {server_list[server_name]}')
        self.choosen_server_name = input("Enter name to join: ")
        # join to the server
        if(self.choosen_server_name in server_list.keys()):
            self.join_server(server_list[self.choosen_server_name])
            self.joined_servers[self.choosen_server_name]=server_list[self.choosen_server_name]
        else:
            print('Entered Name Does not exist')
        
    
    def join_server(self, server_address):
        request={
            'request_type':'join_server',
            'arguments': {
                'unique_id': self.unique_id
            }
        }
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=server_address,
            body=json.dumps(request)
        )
    
    def join_server_success(self, status):
        print(f"JOINING REQUEST: {status}")
        if(status=='FAIL'):
            self.joined_servers.pop(self.choosen_server_name)
        self.terminal_lock.release()

    
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
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.joined_servers[self.choosen_server_name],
            body=json.dumps(request)
        )

    def leave_server_success(self,status):
        self.terminal_lock.acquire()
        print(f"LEAVING REQUEST: {status}")
        if(status=='SUCCESS'):
            self.joined_servers.pop(self.choosen_server_name)
        self.terminal_lock.release()


    def get_server_list(self):
        request={
            'request_type':'get_server_list',
            'arguments': {
                'address': self.unique_id
            }
        }
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.registry_queue_name,
            body=json.dumps(request)
        )


    def show_menu(self):
        while True:
            self.terminal_lock.acquire()
            print("---------MENU--------\n1. Get Server List/join server\n2. Get Joined Servers/Leave Server\n3. Exit\n")
            try:
                choice=int(input('Choose one option: '))

                if(choice==1):
                    self.get_server_list()
                elif(choice==2):
                    self.leave_server()
                elif(choice==3):
                    self.channel.stop_consuming()
                    return
            except:
                print("[ERROR] Incorrect Input")
            finally:
                self.terminal_lock.release()
                sleep(0.2)

def main():
    my_client=client()
    my_client.start()
    my_client.consumer_thread.join()
    

if __name__=='__main__':
    main()