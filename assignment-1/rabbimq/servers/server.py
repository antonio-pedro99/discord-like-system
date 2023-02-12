#code for servers
import pika
import json
import uuid
from time import sleep
from threading import Thread

class server:
    
    # all the connection initialisation for RabbitMQ
    def __init__(self):
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
        

    def register(self):
        self.server_name =input("INPUT NAME OF THE SERVER: ")
        message={
            'request_type':'register',
            'arguments': {
                'name': self.server_name,
                'address': self.server_queue_name
            }
        }
        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=self.registry_queue_name,
            body=json.dumps(message)
        )



def main():
    my_server=server()
    my_server.start()
    

if __name__=='__main__':
    main()