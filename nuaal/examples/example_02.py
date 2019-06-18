from nuaal.Discovery import Neighbor_Discovery
import json
from nuaal.Parsers import CiscoIOSParser

provider = {
    "username": "admin",
    "password": "cisco",
    "enable": True,
    "secret": "cisco",
    "parser": CiscoIOSParser()
}
disc = Neighbor_Discovery(provider=provider, DEBUG=True)
disc.run(ip="192.168.100.181")
print(json.dumps(disc.data, indent=2,))
print(json.dumps(disc.topology, indent=2,))
