from nuaal.Parsers import ParserModule
import timeit
import re

class JuniperJUNOSParser(ParserModule):
    """
    Child class of `ParserModule` designed for `cisco_ios` device type.
    """
    def __init__(self, DEBUG=False):
        super(JuniperJUNOSParser, self).__init__(device_type="juniper_junos", DEBUG=DEBUG)
    