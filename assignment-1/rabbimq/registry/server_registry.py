#registry for servers
import pika
import json

class server_registry:
    
    # all the connection initialisation for RabbitMQ
    def __init__(self):
        # registry attributes
        self.MAXSERVERS=10
        self.current_registered=0
        self.server_list={}
        
        # all the important namings
        self.exchange_name='discord'
        self.registry_queue_name='registry_request'
        self.broker_ip='192.168.139.139'    # default port in use for registry
        
    
    def start(self):
        # basic configuratons for RabbitMQ
        connection=pika.BlockingConnection(pika.ConnectionParameters(self.broker_ip))
        self.channel=connection.channel()
        self.channel.exchange_declare(
            exchange=self.exchange_name, 
            durable=True,
            exchange_type='direct'
        )
        self.setup_registry_queue()

    
    def setup_registry_queue(self):
        # this queue id for handling requests comming in register-server 
        registry_queue=self.channel.queue_declare(
            queue=self.registry_queue_name,
            durable=True
        )
        self.channel.queue_bind(
            exchange=self.exchange_name, 
            queue=registry_queue.method.queue,
            routing_key=self.registry_queue_name
        )
        self.channel.basic_consume(
            queue=registry_queue.method.queue, 
            auto_ack=True, 
            on_message_callback=self.handle_request
        )
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()


    def handle_request(self, ch, method, properties, body):
        request=json.loads(body)        
        if (request['request_type']=='register'):
            self.register(request['arguments'])
        elif (request['request_type']=='get_server_list'):
            self.get_server_list(request['arguments'])
    

    def register(self,args):
        print(f"JOIN REQUEST FROM {args['address']} [ADDRESS]")
        status='FAIL'
        if(self.current_registered<self.MAXSERVERS):
            status='SUCCESS'
            self.server_list[args['name']]=args['address']
            self.current_registered+=1
        self.channel.basic_publish( exchange=self.exchange_name, routing_key=args['address'], 
        body=json.dumps({'request_type':'register', 'response':status}))
    

    def get_server_list(self,args):
        print(f"SERVER LIST REQUEST FROM {args['address']} [ADDRESS]")
        self.channel.basic_publish( exchange=self.exchange_name, routing_key=args['address'], 
        body=json.dumps({'request_type':'get_server_list', 'response':self.server_list}))


def main():
    my_registry=server_registry()
    my_registry.start()
    

if __name__=='__main__':
    main()