from huesdk import Hue

username = Hue.connect(bridge_ip="192.168.1.150")
print(f"HUE USERNAME: {username}")