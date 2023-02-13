#code for servers
import pika
import json
import uuid
from time import sleep
from threading import Thread
import pandas as pd
import datetime

class server:
    
    # all the connection initialisation for RabbitMQ
    def __init__(self):
        # server attributes
        self.MAXCLIENTS=10
        self.CLIENTELE=[]
        self.current_clients=0
        self.article_list=[]
        
        # all the important namings
        self.exchange_name='discord'
        self.registry_queue_name='registry_request'
        self.broker_ip='192.168.139.139'    # default port in use for registry
        self.server_queue_name=str(uuid.uuid1())


    def start(self):
        # basic configuratons for RabbitMQ
        connection=pika.BlockingConnection(pika.ConnectionParameters(self.broker_ip))
        self.channel=connection.channel()
        self.channel.exchange_declare(
            exchange=self.exchange_name, 
            durable=True,
            exchange_type='direct'
        )
        self.consumer_thread=Thread(target=self.setup_server_queue)
        self.consumer_thread.start()
        self.register()
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        self.consumer_thread.join()


    def setup_server_queue(self):
        # this queue id for handling requests comming in register-server 
        server_queue=self.channel.queue_declare(
            queue=self.server_queue_name,
            durable=True
        )
        self.channel.queue_bind(
            exchange=self.exchange_name, 
            queue=server_queue.method.queue,
            routing_key=self.server_queue_name
        )
        self.channel.basic_consume(
            queue=server_queue.method.queue, 
            auto_ack=True, 
            on_message_callback=self.handle_request
        )


    def handle_request(self, ch, method, properties, body):
        request=json.loads(body)
        if (request['request_type']=='register'):
            print('REGISTER REQUEST: ',request['response'])
        elif (request['request_type']=='join_server'):
            self.join_server(request['arguments']['unique_id'])
        elif (request['request_type']=='leave_server'):
            self.leave_server(request['arguments']['unique_id'])
        elif (request['request_type']=='publish_article'):
            self.publish_article(request['arguments'])
        elif (request['request_type']=='get_article'):
            self.get_article(request['arguments'])

    def get_article(self, args):
        
        def convert(x):
            if(x==''):
                return "<BLANK>"
            else:
                return x
        print(f"ARTICLES REQUEST FROM {args['unique_id']} FOR {convert(args['type'])}, {convert(args['author'])}, {convert(args['time'])}")
        try:
            if(args['time'] != ""):
                args['time']=datetime.datetime.strptime(args['time'],"%d/%m/%Y").date()
            for itr in self.article_list:
                if(
                    (args['type']=='' or args['type']==itr.type) and
                    (args['author']=='' or args['author']==itr.author) and
                    (args['time']=='' or args['time']<=itr.time)
                ):
                    response={
                        'type': itr.type,
                        'author': itr.author,
                        'time': itr.time.strftime("%d/%m/%Y"),
                        'content': itr.content
                    }
                    self.channel.basic_publish( exchange=self.exchange_name, routing_key=args['unique_id'], 
                    body=json.dumps({'request_type':'get_article', 'response':response}))
        except:
            self.channel.basic_publish( exchange=self.exchange_name, routing_key=args['unique_id'], 
            body=json.dumps({'request_type':'get_article', 'response':'FAIL'}))

    
    def publish_article(self, args):
        print(f"ARTICLES PUBLISH FROM {args['unique_id']}")
        status='FAIL'
        if(args['unique_id'] in self.CLIENTELE) and args['author']!="" and args['content']!="":
            status='SUCCESS'
            new_article=article(type=args['type'],author=args['author'],content=args['content'])
            self.article_list.append(new_article)
        self.channel.basic_publish( exchange=self.exchange_name, routing_key=args['unique_id'], 
        body=json.dumps({'request_type':'publish_article', 'response':status}))


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
        self.channel.basic_publish( exchange=self.exchange_name, routing_key=client_uuid, 
        body=json.dumps({'request_type':'leave_server', 'response':status}))


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
        self.channel.basic_publish( exchange=self.exchange_name, routing_key=client_uuid, 
        body=json.dumps({'request_type':'join_server', 'response':status}))
    

    def register(self):
        self.server_name =input("INPUT NAME OF THE SERVER: ")
        request={
            'request_type':'register',
            'arguments': {
                'name': self.server_name,
                'address': self.server_queue_name
            }
        }
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.registry_queue_name,
            body=json.dumps(request)
        )


class article:

    def __init__(self,type,author,content):
        self.type=type
        self.author=author
        self.time=pd.Timestamp('now', tz='Asia/Kolkata').date()
        self.content=content


def main():
    my_server=server()
    my_server.start()
    

if __name__=='__main__':
    main()