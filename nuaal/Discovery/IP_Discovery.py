from nuaal.connections.cli import CliMultiRunner
from nuaal.Discovery.Topology import CliTopology
from nuaal.utils import get_logger
from nuaal.Parsers import CiscoIOSParser
import json

class IP_Discovery:
    def __init__(self, provider, DEBUG=False):
        self.DEBUG = DEBUG
        self.logger = get_logger(name="IP_Discovery", DEBUG=self.DEBUG)
        self.provider = provider
        self.data = None
        self.topology = None

    def run(self, ips):
        runner = CliMultiRunner(provider=self.provider, ips=ips, workers=6)
        runner.actions = ["get_neighbors"]
        runner.run()
        self.data = runner.data
        topo = CliTopology()
        topo.build_topology(self.data)
        self.topology = topo.topology

if __name__ == '__main__':
    ips = [
        "192.168.100.181",
        "192.168.100.182",
        "192.168.100.183",
        "192.168.100.184",
        "192.168.100.185",
        "192.168.100.186"
    ]
    provider = {
        "username": "admin",
        "password": "cisco",
        "enable": True,
        "secret": "cisco",
        "parser": CiscoIOSParser()
    }
    disc = IP_Discovery(provider=provider, DEBUG=True)
    disc.run(ips=ips)
    print(json.dumps(disc.topology, indent=2))