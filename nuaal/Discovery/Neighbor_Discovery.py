from nuaal.utils import get_logger
from nuaal.utils import Filter
from nuaal.connections.cli import Cisco_IOS_Cli
import threading
from nuaal.definitions import DATA_PATH
import json
import queue
import timeit
from datetime import datetime

class Neighbor_Discovery:
    """
    This class provides a simple way to perform network discovery based on CDP neighbors of device.
    Given IP address of initial device (or 'seed device') it tries to crawl trough ne network and discover all supported devices.
    CDP must be enabled on devices.
    """
    def __init__(self, provider, DEBUG=False):
        self.DEBUG = DEBUG
        self.logger = get_logger(name="NeighborDiscovery", DEBUG=self.DEBUG)
        self.provider = provider
        self.data = {}
        self.topology = {"nodes": {}, "links": {}}
        self.visited = []
        self.discovered = []
        self.to_process = []
        self.to_visit = []
        self.workers = 4
        self.queue = queue.Queue()
        self.threads = []
        self.current_id = 0
        self.neighbor_filter = Filter(required={"capabilities": ["Router", "Switch"]}, exact_match=False)

    def _gen_device_id(self, ip, hostname=None):
        """
        Function to generate pseudo-unique identification of device. By default, it returns device hostname,
        if hostname is one of the default hostnames, it uses IP address to distinguish devices with same hostname.
        :param ip: String - IP address of the device
        :param hostname: String (optional) - Hostname of the device
        :return: String - such as "C2960X_AB01" or "Router(192.168.1.1)"
        """
        if not hostname:
            return f"({ip})"
        default_hostnames = ["Router", "Switch"]
        if hostname not in default_hostnames:
            return hostname
        else:
            return f"{hostname}({ip})"

    def get_neighbors(self, ip, hostname=None):
        """
        This function performs the discovery of the neighbors for given device. Results are stored in self.to_process.
        After each round, the results are processed by self.process_neigbors()
        :param ip: String - IP Address of the device
        :param hostname: String (optinal) - Hostname of the device, if not given, will be set after connecting to device
        :return:
        """
        device_id = self._gen_device_id(ip=ip)
        start_time = timeit.default_timer()
        if hostname:
            device_id = self._gen_device_id(ip=ip, hostname=hostname)
        device_neighbors = []
        self.logger.info(msg=f"Discovering device {device_id}")
        with Cisco_IOS_Cli(ip=ip, **self.provider) as device:
            if not device.device:
                self.logger.error(msg=f"Could not connect to device {device_id}. Failed after {timeit.default_timer() - start_time} seconds.")
                self.to_process.append({device_id: []})
            else:
                device_id = self._gen_device_id(ip=ip, hostname=device.data["hostname"])
                if device_id not in self.discovered:
                    self.logger.warning(msg=f"Device {device_id} is being visited, but it is not in discovered. This happens only for seed device.")
                    self.discovered.append(device_id)
                try:
                    device_neighbors = device.get_neighbors(output_filter=self.neighbor_filter, strip_domain=True)
                except Exception as e:
                    self.logger.error(msg=f"Could not retrieve neighbors of {device_id}. Reason: {repr(e)}. {timeit.default_timer() - start_time} seconds.")
                finally:
                    if {device_id: device_neighbors} in self.to_process:
                        print("THIS SHOULD NOT HAPPEN!")
                    self.logger.debug(msg=f"Storing results from {device_id} for later processing. Time: {timeit.default_timer() - start_time} seconds.")
                    self.to_process.append({device_id: device_neighbors})
                    try:
                        self.to_visit.remove({device_id: {"ip": ip, "hostname": hostname}})
                    except ValueError:
                        self.logger.debug(msg=f"Could not remove device {device_id} from self.to_visit. Item not in list.")
                    except Exception as e:
                        print(repr(e))

    def process_neighbors(self):
        """
        This functions decides what to do with neighbors of device, such as which were already discovered or visited.
        It runs after every discovery round to combine data retrieved by individual worker threads.
        :return:
        """
        start_time = timeit.default_timer()
        for item in self.to_process:
            # 'item' represents neighbors of device
            for device_id, neighbors in item.items():
                if device_id in self.visited:
                    print("This should not happen!")
                else:
                    self.visited.append(device_id)
                    self.logger.debug(msg=f"Device {device_id} has been visited.")
                self.logger.info(msg=f"Processing {len(neighbors)} neighbor(s) of device {device_id}")
                self.data[device_id] = neighbors
                for neighbor in neighbors:
                    neighbor_id = self._gen_device_id(ip= neighbor["ipAddress"], hostname=neighbor["hostname"])
                    if neighbor_id in self.visited:
                        self.logger.info(msg=f"Neighbor {neighbor_id} of device {device_id} has already been visited.")
                        continue
                    elif neighbor_id in self.discovered:
                        self.logger.info(msg=f"Neighbor {neighbor_id} of device {device_id} has already been discovered, waiting to be visited.")
                        continue
                    else:
                        self.logger.info(msg=f"Discovered new neighbor {neighbor_id} of device {device_id}.")
                        self.discovered.append(neighbor_id)
                        self.to_visit.append({neighbor_id: {"ip": neighbor["ipAddress"], "hostname": neighbor["hostname"]}})
                        self.queue.put({"ip": neighbor["ipAddress"], "hostname": neighbor["hostname"]})
        self.to_process = []
        self.logger.info(msg=f"All outputs of current round have been processed. Time: {timeit.default_timer() - start_time} seconds.")

    def worker(self):
        """
        This is a wrapper function that is run as thread.
        :return:
        """
        self.logger.debug(msg=f"Thread {threading.current_thread().getName()} started.")
        if self.queue.empty():
            self.logger.debug(msg=f"No work for thread {threading.current_thread().getName()}.")
        while not self.queue.empty():
            params = self.queue.get()
            if params is None:
                break
            self.get_neighbors(**params)
            self.queue.task_done()

    def run(self, ip):
        self.get_neighbors(ip=ip)
        self.process_neighbors()
        while len(self.to_visit) > 0:
            try:
                for i in range(self.workers):
                    t = threading.Thread(name=f"DiscoveryThread-{i}", target=self.worker)
                    self.threads.append(t)
                [t.start() for t in self.threads]
                self.queue.join()
                self.threads = []
                self.process_neighbors()
            except KeyboardInterrupt:
                self.logger.info(msg="Keyboard Interrupt")
                break
            finally:
                self.process_neighbors()
        with open(f"{DATA_PATH}\discovery\{ip}-{str(datetime.now()).replace(':', '-')}.json", mode="w") as f:
            json.dump(self.data, f, indent=2)

if __name__ == '__main__':
    provider = {
        "method": "ssh",
        "store_outputs": True,
        "DEBUG": True,
        "enable": True,
        "username": "admin",
        "password": "cisco",
        "secret": "cisco"
    }
    dis = Neighbor_Discovery(provider=provider, DEBUG=True)
    dis.run(ip="192.168.100.181")
    print(dis.data)