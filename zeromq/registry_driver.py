from components.server_registry import ServerRegistry

def main():
    registry =  ServerRegistry()
    registry.start()

if __name__ == '__main__':
    main()