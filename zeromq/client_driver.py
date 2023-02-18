from components.client import Client
from time import sleep

def main():
    my_client=Client()
    my_client.start()
    show_menu(my_client)


def show_menu(client):
    while True:
        client.terminal_lock.acquire()
        print("\n---------MENU--------\n1. Get Server List/join server\n2. Get Joined Servers/Leave Server\n3. Publish Article\n4. Get Articles\n5. Exit\n")
        try:
            choice=int(input('Choose one option: '))
            if(choice==1):
                client.get_server_list()
            elif(choice==2):
                client.leave_server()
            elif(choice==3):
                client.publish_article()
            elif(choice==4):
                client.get_article()
            elif(choice==5):
                client.consumer_thread.join()
                return
        except ValueError:
            print("[ERROR] Incorrect Input")
        finally:
            client.terminal_lock.release()
            sleep(0.2)

if __name__=='__main__':
    main()