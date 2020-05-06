import gatt

manager = gatt.DeviceManager(adapter_name='hci0')

mac_pycom = '30:AE:A4:50:5D:2A' # The ambient sensor MAC

class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        # Print services provided by the pycom device
        print("[%s] Resolved services" % (self.mac_address))
        for service in self.services:
            print("[%s]  Service [%s]" % (self.mac_address, service.uuid))
            for characteristic in service.characteristics:
                print("[%s]    Characteristic [%s]" % (self.mac_address, characteristic.uuid))


        # Get the service
        ambient_sensor_service = next(
            s for s in self.services
            if s.uuid == '31313131-3131-3131-3131-313131313131')

        # Get the characteristic
        lux_characteristic = next(
            c for c in ambient_sensor_service.characteristics
            if c.uuid == '32323232-3232-3232-3232-323232323232')

        print("Reading lux value")
        # Read the characteristic
        lux_characteristic.read_value()

    def characteristic_value_updated(self, characteristic, value):
        print("Characteristic value updated.. Trying to decode")
        print("Lux value:", value.decode("utf-8"))


device = AnyDevice(mac_address=mac_pycom, manager=manager)
device.connect()

manager.run()