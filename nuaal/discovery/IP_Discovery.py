from nuaal.connections.cli import CliMultiRunner
from nuaal.discovery.Topology import CliTopology
from nuaal.utils import get_logger
from nuaal.Parsers import CiscoIOSParser
import json

class IP_Discovery(object):
    """
    This function performs discovery of the network devices based on their IP addresses.
    """
    def __init__(self, provider, DEBUG=False, verbosity=3, netmiko_params={}):
        """

        :param dict provider: Provider dictionary containing information for creating connection object, such as credentials
        :param bool DEBUG: Enables debugging output
        """
        self.DEBUG = DEBUG
        self.logger = get_logger(name="IP_Discovery", DEBUG=self.DEBUG, verbosity=verbosity)
        self.provider = provider
        self.netmiko_params = netmiko_params
        self.data = None
        self.topology = None

    def run(self, ips):
        """
        Main entry function. Starts the discovery process based on given IP address of the seed device.

        :param list ips: List of IP addresses for discovery
        :return: ``None``
        """
        runner = CliMultiRunner(provider=self.provider, ips=ips, workers=6, netmiko_params=self.netmiko_params)
        runner.actions = ["get_neighbors"]
        runner.run()
        self.data = runner.data
        topo = CliTopology()
        topo.build_topology(self.data)
        self.topology = topo.topology
