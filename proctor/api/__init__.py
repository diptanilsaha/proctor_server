from .base import api
from .resources import usb, register

api.add_resource(register.ClientRegister, '/clientRegister/')
api.add_resource(usb.UsbIncident, '/usbIncident/')
