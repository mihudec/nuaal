import logging
from nuaal.connections.cli.CliBase import CliBaseConnection
from nuaal.connections.cli.Cisco_IOS_Cli import Cisco_IOS_Cli
from nuaal.connections.cli.CliMultiRunner import CliMultiRunner
# Disable error logging for Paramiko library
logging.getLogger("paramiko").setLevel(logging.CRITICAL)
