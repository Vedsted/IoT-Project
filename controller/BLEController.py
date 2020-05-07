from bluepy.btle import Peripheral
import _thread

class BLEController:

    def __init__(self, delegate):
        # Variables
        self.delegate = delegate

    def connect(self, server_mac):
        self.server_mac = server_mac
        self.peripheral = Peripheral(self.server_mac)
        self.peripheral.setDelegate(self.delegate)
        self.listening = False

    def disconnect(self):
        self.peripheral.disconnect()

    def print_services(self, primary_service_uuid):
        svcs = self.peripheral.getServices()
        
        print("Services:")
        for s in svcs:
            print(s)

        print("Characteristics:")
        svc = self.peripheral.getServiceByUUID(primary_service_uuid)
        chs = svc.getCharacteristics()
        for c in chs:
            print(str(c) + " handle: " + str(c.getHandle()))
        
    def listen(self):
        if not self.listening:
            self.listening = True
            while self.listening:
                if self.peripheral.waitForNotifications(1.0):
                    # handleNotification() was called
                    continue
                print('Listening...')

    def listen_async(self):
        raise Exception("Not Implemented")
        #self.listen_thread = _thread.start_new_thread(self.listen, ())


    def stop_listening(self):
        self.listening = False