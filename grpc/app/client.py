import grpc
import services_pb2 as message
import services_pb2_grpc as servicer
from concurrent import futures
import uuid
import pandas as pd


class ClientService():

    def __init__(self) -> None:
        self.unique_id=str(uuid.uuid1())
        self.joined_servers={}
        self.registry_channel=grpc.insecure_channel('localhost:50001')
        self.register_stub = servicer.ServerRegistryStub(self.registry_channel)
        self.client=message.Client(id=self.unique_id)
        print('CLIENT STARTED')


    def GetServerList(self):
        response = self.register_stub.GetServerList(message.Client(id=self.unique_id))
        print('----------------\nLIST OF AVAILABLE SERVERS')
        for server in response.serverList:
             print(f'{server.name} {server.address}')
        self.choosen_server_name = input("Enter name to join: ")
        # join to the server
        index=list([server.name for server in response.serverList]).index(self.choosen_server_name)
        if(index != -1):
            self.JoinServer(name=self.choosen_server_name, address=response.serverList[index].address)
        else:
            print('Entered Name Does not exist')


    def JoinServer(self, name, address):
        server_channel=grpc.insecure_channel(address)
        self.joined_servers[name] = servicer.ServerStub(server_channel)
        response=self.joined_servers[name].JoinServer(self.client)
        print(f"JOINING REQUEST: {self.status(response.status)}")
        if(self.status(response.status)=='FAIL'):
            self.joined_servers.pop(name)


    def LeaveSever(self):
        print("----------------\nJOINED SERVERS ARE:")
        for server_name in self.joined_servers.keys():
            print(server_name)
        self.choosen_server_name=input("Enter name to leave: ")
        if(self.choosen_server_name not in self.joined_servers.keys()):
            print("Entered Name Does not exist")
            return
        response=self.joined_servers[self.choosen_server_name].LeaveSever(self.client)
        print(f"LEAVING REQUEST: {self.status(response.status)}")
        if(self.status(response.status)=='SUCCESS'):
            self.joined_servers.pop(self.choosen_server_name)


    def PublishArticle(self):
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

        new_article=message.Article(author=author, 
                                    time='',
                                    content=content)
        new_article._type=types[choosen_type-1]
        response=self.joined_servers[choosen_server].PublishArticle(
            message.ArticleRequest(client=self.client, article=new_article)
        )
        print(f"PUBLISHING REQUEST: {self.status(response.status)}")


    def GetArticle(self):
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
        article_for_request=message.Article(author=author, time=time, content='')
        article_for_request._type=types[choosen_type-1]
        response=self.joined_servers[choosen_server].GetArticle(message.ArticleRequest(
            client=self.client, article=article_for_request
        ))
        if(len(response.articleList)==0):
            print("NO ARTICLE TO SHOW")
            return
        else:
            for article in response.articleList:
                print("------------------")
                print(f"Type: {article._type}\nAuthor: {article.author}\nDate: {article.time}")
                print(f"Content: {article.content}")
        

    def status(self, code):
        if code==0:
            return 'SUCCESS'
        else:
            return 'FAIL'


def main():
    my_client=ClientService()


if __name__=='__main__':
    main()