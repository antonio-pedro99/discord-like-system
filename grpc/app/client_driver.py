from client import ClientService

def main():
    my_client=ClientService()
    show_menu(my_client)


def show_menu(client):
    while True:
        print("\n---------MENU--------\n1. Get Server List/join server")
        print("2. Get Joined Servers/Leave Server\n3. Publish Article\n4. Get Articles\n5. Exit\n")
        try:
            choice=int(input('Choose one option: '))
            if(choice==1):
                client.GetServerList()
            elif(choice==2):
                client.LeaveSever()
            elif(choice==3):
                client.PublishArticle()
            elif(choice==4):
                client.GetArticle()
            elif(choice==5):
                print("EXITING")
                return
        except ValueError:
            print("[ERROR] Incorrect Input")

if __name__=='__main__':
    main()