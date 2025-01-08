class Device():
    def __init__(self, serial, addr, port):
        self.serial = serial
        self.address = addr
        self.port = port

    def get_serial(self):
        return self.serial

    def get_address(self):
        return self.address

    def get_port(self):
        return self.port
