from nuaal.connections.cli  import Cisco_IOS_Cli


def GetCliHandler(device_type=None, ip=None, username=None, password=None, parser=None, secret=None, enable=False, store_outputs=False, DEBUG=False):
    if device_type == "cisco_ios":
        return Cisco_IOS_Cli(ip=ip, username=username, password=password, parser=parser, secret=secret, enable=enable, store_outputs=store_outputs, DEBUG=DEBUG)
