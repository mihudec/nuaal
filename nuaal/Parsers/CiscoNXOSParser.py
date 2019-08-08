from nuaal.Parsers import ParserModule
import timeit
import re

class CiscoNXOSParser(ParserModule):
    """
    Child class of `ParserModule` designed for `cisco_ios` device type.
    """
    def __init__(self, DEBUG=False):
        super(CiscoNXOSParser, self).__init__(device_type="cisco_nxos", DEBUG=DEBUG)
