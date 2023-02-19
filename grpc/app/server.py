import grpc
import services_pb2 as message
import services_pb2_grpc as servicer
from concurrent import futures
from threading import Lock
from port import get_new_port


class ServerService(servicer.ServerServicer):

    def __init__(self) -> None:
        super().__init__()
        self.address='localhost:'+str(get_new_port())
        self.MAXCLIENTS=10
        self.CLIENTELE=[]
        self.current_clients=0
        self.article_list=[]
        self.client_lock=Lock()
        self.article_lock=Lock()
        self.registry_channel=grpc.insecure_channel('localhost:50001')


    def start(self):
        try:
            self.SetupServer()
            self.RegisterServer()
        except KeyboardInterrupt:
            print('CLOSING REGISTRY')
            return


    def SetupServer(self):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=self.MAXCLIENTS))
        servicer.add_ServerServicer_to_server(ServerService(),self.server)
        print("REGISTRY STARTED")
        self.server.add_insecure_port(self.address)


    def RegisterServer(self):
        self.name=input("INPUT NAME OF THE SERVER: ")
        register_server_stub = servicer.ServerRegistryStub(self.registry_channel)
        response = register_server_stub.RegisterServer(
            message.ServerMessage(name=self.name,address=self.address)
        )
        print('REGISTER REQUEST: ',self.status(response.status))
        self.server.start()
        self.server.wait_for_termination()


    def JoinServer(self, request, context):
        print(f'JOIN REQUEST FROM {request.id}')
        status='FAIL'
        try:
            if (request.id in self.CLIENTELE):
                status='SUCCESS'
            else:
                if (self.current_clients<self.MAXCLIENTS):
                    status='SUCCESS'
                    self.CLIENTELE.append(request.id)
                    self.current_clients+=1
        except:
            pass
        return message.Result(status=status)
    

    def LeaveSever(self, request, context):
        print(f'LEAVE REQUEST FROM {request.id}')
        status='FAIL'
        try:
            status='SUCCESS'
            if(request.id in self.CLIENTELE):
                self.CLIENTELE.remove(request.id)
                self.current_clients-=1
        except:
            pass
        return message.Result(status=status)
    
    
    def PublishArticle(self, request, context):
        print(f"ARTICLES PUBLISH FROM {request.client.id}")
        status='FAIL'
        if(request.client.id in self.CLIENTELE) and request.article.author!="" and request.article.content!="":
            status='SUCCESS'
            # new_article=message.Article() article(type=args['type'],author=args['author'],content=args['content'])
            # self.article_list.append(new_article)

        return super().PublishArticle(request, context)
    
    def GetArticle(self, request, context):
        return super().GetArticle(request, context)


    def status(self, code):
        if code==0:
            return 'SUCCESS'
        else:
            return 'FAIL'

def main():
    my_server=ServerService()
    my_server.start()
    return


if __name__=='__main__':
    main()