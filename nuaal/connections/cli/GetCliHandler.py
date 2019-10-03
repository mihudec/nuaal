from nuaal.connections.cli import Cisco_IOS_Cli


def GetCliHandler(device_type=None, ip=None, username=None, password=None, parser=None, secret=None, enable=False, store_outputs=False, DEBUG=False, verbosity=3):
    """
    This function can be used for getting the correct connection object for specific device type.

    :param str device_type: String representation of device type, such as `cisco_ios`
    :param ip: (str) IP address or FQDN of the device you're trying to connect to
    :param username: (str) Username used for login to device
    :param password: (str) Password used for login to device
    :param parser: (ParserModule) Instance of ParserModule class which will be used for parsing of text outputs. By default, new instance of ParserModule is created.
    :param secret: (str) Enable secret for accessing Privileged EXEC Mode
    :param enable: (bool) Whether or not enable Privileged EXEC Mode on device
    :param store_outputs: (bool) Whether or not store text outputs of sent commands
    :param DEBUG: (bool) Enable debugging logging
    :return: Instance of connection object
    """
    if device_type == "cisco_ios":
        return Cisco_IOS_Cli(ip=ip, username=username, password=password, parser=parser, secret=secret, enable=enable, store_outputs=store_outputs, DEBUG=DEBUG, verbosity=verbosity)
