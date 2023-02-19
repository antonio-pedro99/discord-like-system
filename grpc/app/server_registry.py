import grpc
import services_pb2 as message
import services_pb2_grpc as servicer
from concurrent import futures
from threading import Lock

class ServerRegistryService(servicer.ServerRegistryServicer):

    def __init__(self) -> None:
        super().__init__()
        self.MAXSERVERS=10
        self.current_registered=0
        self.server_list={}
        self.server_list_lock=Lock()

    def RegisterServer(self, request, context):
        self.server_list_lock.acquire()
        print(f"JOIN REQUEST FROM {request.address} [ADDRESS]")
        status='FAIL'
        if(self.current_registered<self.MAXSERVERS):
            status='SUCCESS'
            self.server_list[request.name]=message.ServerMessage(name=request.name,address=request.address)
            self.current_registered+=1
        self.server_list_lock.release()
        return message.Result(status=status)
    
    def GetServerList(self, request, context):
        self.server_list_lock.acquire()
        print(f"SERVER LIST REQUEST FROM {request.id} [ADDRESS]")
        all_servers=message.ServerList()
        all_servers.serverList.extend(list(self.server_list.values()))
        self.server_list_lock.release()
        return all_servers


def main():
    try:
        print("STARTING REGISTRY")
        registry_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        servicer.add_ServerRegistryServicer_to_server(ServerRegistryService(),registry_server)
        print("REGISTRY STARTED")
        registry_server.add_insecure_port('localhost:50001')
        registry_server.start()
        registry_server.wait_for_termination()
    except KeyboardInterrupt:
        print("------CLOSING REGISTRY------")
        return


if __name__=='__main__':
    main()