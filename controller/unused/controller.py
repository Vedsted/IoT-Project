#
# Prerequisites:
# https://github.com/getsenic/gatt-python
#
import gatt
import uuid

#mac_pycom = '30:AE:A4:50:5D:2A' # The ambient sensor MAC
service_uuid = str(uuid.UUID(bytes=b'1111222233334444')) # Find the device with a service with this UUID
primary_service_uuid = str(uuid.UUID(bytes=b'2222222222222222')) # UUID of the primary service
lux_characteristic_uuid = str(uuid.UUID(bytes=b'3333333333333333'))

class AnyDeviceManager(gatt.DeviceManager):
    def device_discovered(self, device):

        print("Discovered [%s] %s" % (device.mac_address, device.alias()))
        #self.stop_discovery()



class AnyDevice(gatt.Device):
    def device_discovered(self, device):
        print("Discovered [%s] %s" % (device.mac_address, device.alias()))

    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def characteristic_enable_notifications_succeeded(self, characteristic):
        print("Enabling Notifications succeded")

    def characteristic_enable_notifications_failed(self, characteristic, error):
        print("Enabling Notifications failed")
        print(error)

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
            if s.uuid == primary_service_uuid)

        # Get the characteristic
        lux_characteristic = next(
            c for c in ambient_sensor_service.characteristics
            if c.uuid == lux_characteristic_uuid)

        print("Reading lux value")
        # Enable notifications
        lux_characteristic.enable_notifications()

    def characteristic_value_updated(self, characteristic, value):
        print("Characteristic value updated.. Trying to decode")
        print("Lux value:", value.decode("utf-8"))


manager = AnyDeviceManager(adapter_name='hci0')
#device = AnyDevice(mac_address=mac_pycom, manager=manager)

manager.start_discovery([service_uuid]) # The sensor has to be discovered before we can connect to it
manager.run() # Has to be called to start the event loop