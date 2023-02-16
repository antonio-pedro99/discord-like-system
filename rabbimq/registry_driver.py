from components.server_registry import ServerRegistry

def main():
    my_registry=ServerRegistry()
    my_registry.start()

if __name__=='__main__':
    main()