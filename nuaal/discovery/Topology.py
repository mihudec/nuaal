from nuaal.utils import get_logger
from nuaal.definitions import DATA_PATH
import json


class Topology(object):
    def __init__(self, DEBUG=False):
        self.DEBUG = DEBUG
        self.logger = get_logger(name="Topology", DEBUG=DEBUG)
        self.topology = {"nodes": [], "links": []}

    def next_ui(self):
        id_couter = 0
        next_topo = {"nodes": [], "links": []}
        id_map = {}
        for node in self.topology["nodes"]:
            id_map[node] = id_couter
            next_topo["nodes"].append({"id": id_couter, "name": node})
            id_couter += 1
        for link in self.topology["links"]:
            next_topo["links"].append({"source": id_map[link["sourceNode"]], "target": id_map[link["targetNode"]]})
        return next_topo


class CliTopology(Topology):
    def __init__(self, DEBUG=False):
        super(CliTopology, self).__init__(DEBUG=DEBUG)

    def build_topology(self, data):
        if isinstance(data, list):
            data = {x["hostname"]: x["neighbors"] for x in data}
        elif isinstance(data, dict):
            data = {k: data[k]["neighbors"] for k in data.keys()}
        
        self.logger.info(msg="Building topology based on {} visited devices.".format(len(data)))
        all_nodes = []
        all_links = []
        for device_id, neighbors in data.items():
            links = self._get_links(device_id=device_id, neighbors=neighbors)
            if device_id not in all_nodes:
                all_nodes.append(device_id)
            for neighbor_id in [x["targetNode"] for x in links]:
                if neighbor_id not in all_nodes:
                    all_nodes.append(neighbor_id)
            for link in links:
                if link not in all_links and self._reverse_link(link) not in all_links:
                    all_links.append(link)
        self.topology["links"] = all_links
        self.topology["nodes"] = all_nodes
        self.logger.info(msg="Discovered total of {} nodes and {} links".format(len(all_nodes), len(all_links)))

    def _get_links(self, device_id, neighbors):
        links = []
        for neighbor in neighbors:
            link = {
                "sourceNode": device_id,
                "sourceInterface": neighbor["localInterface"],
                "targetNode": neighbor["hostname"],
                "targetInterface": neighbor["remoteInterface"]
            }
            links.append(link)
        return links

    def _reverse_link(self, link):
        reverse_link = {
            "sourceNode": link["targetNode"],
            "sourceInterface": link["targetInterface"],
            "targetNode": link["sourceNode"],
            "targetInterface": link["sourceInterface"]
            }
        return reverse_link