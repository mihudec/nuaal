from nuaal.Parsers import ParserModule


class CiscoIOSParser(ParserModule):
    def __init__(self, DEBUG=False):
        super(CiscoIOSParser, self).__init__(device_type="cisco_ios", DEBUG=DEBUG)