import grpc
import services_pb2 as message
import services_pb2_grpc as servicer
import pandas as pd
import datetime
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
            print('-----CLOSING SERVER------')
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
        self.client_lock.acquire()
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
        self.client_lock.release()
        return message.Result(status=status)
    

    def LeaveSever(self, request, context):
        self.client_lock.acquire()
        print(f'LEAVE REQUEST FROM {request.id}')
        status='FAIL'
        try:
            status='SUCCESS'
            if(request.id in self.CLIENTELE):
                self.CLIENTELE.remove(request.id)
                self.current_clients-=1
        except:
            pass
        self.client_lock.release()
        return message.Result(status=status)
    
    
    def PublishArticle(self, request, context):
        self.article_lock.acquire()
        print(f"ARTICLES PUBLISH FROM {request.client.id}")
        status='FAIL'
        if(request.client.id in self.CLIENTELE) and request.article.author!="" and request.article.content!="":
            status='SUCCESS'
            request.article.time=str(pd.Timestamp('now', tz='Asia/Kolkata').date())
            self.article_list.append(request.article)
        self.article_lock.release()
        return message.Result(status=status)
    

    def GetArticle(self, request, context):
        def convert(x):
            if(x==''):
                return "<BLANK>"
            else:
                return x
        
        self.article_lock.acquire()
        articles_to_send=message.ArticleList()
        print(f"ARTICLES REQUEST FROM {request.client.id} FOR {convert(request.article._type)}, {convert(request.article.author)}, {convert(request.article.time)}")
        try:
            if(request.article.time != ""):
                requested_time=datetime.datetime.strptime(request.article.time,"%d/%m/%Y").date()
            for itr in self.article_list:
                if(
                    (request.article._type=='' or request.article._type==itr._type) and
                    (request.article.author=='' or request.article.author==itr.author) and
                    (request.article.time=='' or requested_time<=datetime.datetime.strptime(itr.time, "%Y-%m-%d").date())
                ):
                    articles_to_send.articleList.append(itr)
        except:
            pass
        self.article_lock.release()
        return articles_to_send


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