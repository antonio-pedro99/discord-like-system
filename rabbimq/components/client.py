#code for client
import pika
import json
import uuid
from time import sleep
from threading import Thread, Lock
import datetime 

class Client:

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
        elif (request['request_type']=='publish_article'):
            self.publish_article_success(request['response'])
        elif (request['request_type']=='get_article'):
            self.get_article_success(request['response'])


    def print_server_list(self, server_list):
        self.terminal_lock.acquire()
        print('----------------\nLIST OF AVAILABLE SERVERS')
        for server_name in server_list.keys():
             print(f'{server_name} {server_list[server_name]}')
        self.choosen_server_name = input("Enter name to join: ")
        # join to the server
        if(self.choosen_server_name in server_list.keys()):
            self.joined_servers[self.choosen_server_name]=server_list[self.choosen_server_name]
            self.join_server(server_list[self.choosen_server_name])
        else:
            print('Entered Name Does not exist')
            self.terminal_lock.release()
        
    
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

    
    def publish_article(self):
        types = ['SPORTS', 'FASHION', 'POLITICS']
        print("------------------")
        print("Available Types\n1. SPORTS\n2. FASHION\n3. POLITICS")
        choosen_type=int(input('Choose one Type: '))
        if(choosen_type<=0 or choosen_type>3):
            print("[ERROR] Invalid Type")
            return
        author=input("Enter Author's name: ")
        content=input("Enter Content: ")
        print("JOINED SERVERS ARE:")
        for server_name in self.joined_servers.keys():
            print(server_name)
        choosen_server=input("Enter sever name to publish article: ")
        if(choosen_server not in self.joined_servers.keys()):
            print("[ERROR] invalid server name.")
            return
        request={
            'request_type':'publish_article',
            'arguments': {
                'unique_id': self.unique_id,
                'type': types[choosen_type-1],
                'author': author,
                'content': content
            }
        }
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.joined_servers[choosen_server],
            body=json.dumps(request)
        )


    def publish_article_success(self,status):
        self.terminal_lock.acquire()
        print(f"PUBLISHING REQUEST: {status}")
        self.terminal_lock.release()


    def get_article(self):
        types = ['SPORTS', 'FASHION', 'POLITICS', '']
        print("------------------")
        print("Available Types\n1. SPORTS\n2. FASHION\n3. POLITICS\n4. ALL")
        choosen_type=int(input('Choose one Type: '))
        if(choosen_type<=0 or choosen_type>4):
            print("[ERROR] Invalid Type")
            return
        author=input("Enter Author's name: ")
        time=input("Enter start date (in DD/MM/YYYY): ") 
        print("JOINED SERVERS ARE:")
        for server_name in self.joined_servers.keys():
            print(server_name)
        choosen_server=input("Enter sever name to get article: ")
        if(choosen_server not in self.joined_servers.keys()):
            print("[ERROR] invalid server name.")
            return
        request={
            'request_type':'get_article',
            'arguments': {
                'unique_id': self.unique_id,
                'type': types[choosen_type-1],
                'author': author,
                'time': time
            }
        }
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.joined_servers[choosen_server],
            body=json.dumps(request)
        )


    def get_article_success(self,args):
        if(args=='FAIL'):
            print(args)
            self.terminal_lock.release()
            return
        elif(args=='START'):
            self.terminal_lock.acquire()
        elif(args=='END'):
            self.terminal_lock.release()
        else:
            print("------------------")
            print(f"Type: {args['type']}\nAuthor: {args['author']}\nDate: {args['time']}")
            print(f"Content: {args['content']}")


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

