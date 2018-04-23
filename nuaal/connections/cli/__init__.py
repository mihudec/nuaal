import logging
# Disable error logging for Paramiko library
logging.getLogger("paramiko").setLevel(logging.CRITICAL)
from nuaal.connections.cli.Cisco_IOS_Cli import Cisco_IOS_Cli