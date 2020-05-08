from bluepy.btle import Peripheral
import _thread

class BLEController:

    def __init__(self, delegate):
        # Variables
        self._delegate = delegate

    def connect(self, server_mac):
        self._server_mac = server_mac
        self._peripheral = Peripheral(self._server_mac)
        self._peripheral.setDelegate(self._delegate)
        self._listening = False

    def disconnect(self):
        self._peripheral.disconnect()

    def print_services(self, primary_service_uuid):
        svcs = self._peripheral.getServices()
        
        print("Services:")
        for s in svcs:
            print(s)

        print("Characteristics:")
        svc = self._peripheral.getServiceByUUID(primary_service_uuid)
        chs = svc.getCharacteristics()
        for c in chs:
            print(str(c) + " handle: " + str(c.getHandle()))
        
    def listen(self):
        if not self._listening: # Are we listening already?
            self._listening = True
            while self._listening:
                if self._peripheral.waitForNotifications(1.0):  # Calls the delegate if true
                    # Delegate was called
                    continue
                print('BLEController.listen() -> Listening...')

    def listen_async(self):
        #raise Exception("Not Implemented")
        self._listen_thread = _thread.start_new_thread(self.listen, ())

    def adjust_light_source(self, value):
        # value is a tuple of RGB i.e. (255, 255, 255)

        # BLE characteristic expects a byte array
        value_bytes = bytes(value)
        print("BLEController.adjust_light_source -> {}".format(value_bytes))

        handle = 49 # The handle value has to be found using e.g. print_services(), bluez, or similar
        self._peripheral.writeCharacteristic(handle, value_bytes)


    def stop_listening(self):
        self._listening = False