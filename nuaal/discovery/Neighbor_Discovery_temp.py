from nuaal.utils import get_logger, write_output, Filter
from nuaal.connections.cli import Cisco_IOS_Cli
from nuaal.discovery.Topology import CliTopology
import threading
from nuaal.definitions import OUTPUT_PATH
import json
import queue
import timeit
import pathlib
from datetime import datetime


class Neighbor_Discovery(object):
    """
    This class provides a simple way to perform network discovery based on CDP neighbors of device.
    Given IP address of initial device (or 'seed device') it tries to crawl trough ne network and discover all supported devices.
    CDP must be enabled on devices.
    """
    def __init__(self, provider, max_depth=16, workers=4, verbosity=1, DEBUG=False, netmiko_params={}):
        """

        :param dict provider: Provider dictionary containing information for creating connection object, such as credentials
        :param int max_depth: Maximum depth of discovery in terms of distance (hops) from seed device. Eg. max_depth=1 means,
        that the discovery will stop after direct neighbors of seed have been visited.
        :param bool DEBUG: Enables/disables debugging output
        """
        self.DEBUG = DEBUG
        self.logger = get_logger(name="NeighborDiscovery", DEBUG=self.DEBUG, verbosity=verbosity)
        self.provider = provider
        self.netmiko_params = netmiko_params
        self.data = {}
        self.topology = None
        self.visited = []
        self.discovered = []
        self.to_process = []
        self.to_visit = []
        self.failed = []
        self.workers = workers
        self.queue = queue.Queue()
        self.threads = []
        self.current_id = 0
        self.current_depth = 0
        self.max_depth = max_depth
        self.discover_filter = Filter(required={"capabilities": ["Router", "Switch"], "vendor": ["Cisco"]}, exact_match=False)
        self.neighbor_filter = Filter(excluded={"capabilities": ["Host"]}, exact_match=False)

    def _gen_device_id(self, ip, hostname=None):
        """
        Function to generate pseudo-unique identification of device. By default, it returns device hostname,
        if hostname is one of the default hostnames, it uses IP address to distinguish devices with same hostname.

        :param ip: String - IP address of the device
        :param hostname: String (optional) - Hostname of the device
        :return: String - such as "C2960X_AB01" or "Router(192.168.1.1)"
        """
        if not hostname:
            return "({})".format(ip)
        default_hostnames = ["Router", "Switch"]
        if hostname not in default_hostnames:
            return hostname
        else:
            return "{}({})".format(hostname, ip)

    def get_neighbors(self, ip, hostname=None):
        """
        This function performs the discovery of the neighbors for given device. Results are stored in self.to_process.
        After each round, the results are processed by self.process_neigbors()

        :param ip: String - IP Address of the device
        :param hostname: String (optinal) - Hostname of the device, if not given, will be set after connecting to device
        :return: ``None``
        """
        device_id = self._gen_device_id(ip=ip)
        start_time = timeit.default_timer()
        if hostname:
            device_id = self._gen_device_id(ip=ip, hostname=hostname)
        device_neighbors = []
        self.logger.info(msg="Visiting device {}".format(device_id))
        with Cisco_IOS_Cli(ip=ip, **self.provider, netmiko_params=self.netmiko_params) as device:
            if not device.device:
                self.logger.error(msg="Could not connect to device {}. Failed after {} seconds.".format(device_id, timeit.default_timer() - start_time))
                self.to_process.append({device_id: []})
                self.failed.append(device_id)
            else:
                device_id = self._gen_device_id(ip=ip, hostname=device.data["hostname"])
                if device_id not in self.discovered:
                    self.logger.warning(msg="Device {} is being visited, but it is not in discovered. This happens only for seed device.".format(device_id))
                    self.discovered.append(device_id)
                try:
                    device_neighbors = device.get_neighbors(output_filter=self.neighbor_filter, strip_domain=True)
                    self.custom_commands(device=device)
                    self.data[device_id] = device.data
                except Exception as e:
                    self.logger.error(msg="Could not retrieve neighbors of {}. Reason: {}. {} seconds.".format(device_id, repr(e), timeit.default_timer() - start_time))
                finally:
                    if {device_id: device_neighbors} in self.to_process:
                        print("THIS SHOULD NOT HAPPEN!")
                        self.logger.warning(msg="Revisited device: {}".format(str({device_id: device_neighbors})))
                    self.logger.debug(msg="Storing results from {} for later processing. Time: {} seconds.".format(device_id, timeit.default_timer() - start_time))
                    self.to_process.append({device_id: device_neighbors})
            try:
                self.to_visit.remove({device_id: {"ip": ip, "hostname": hostname}})
            except ValueError:
                self.logger.debug(msg="Could not remove device {} from self.to_visit. Item not in list.".format(device_id))
            except Exception as e:
                print(repr(e))

    def custom_commands(self, device):
        pass

    def process_neighbors(self):
        """
        This functions decides what to do with neighbors of device, such as which were already discovered or visited.
        It runs after every discovery round to combine data retrieved by individual worker threads.

        :return: ``None``
        """
        start_time = timeit.default_timer()
        for item in self.to_process:
            # 'item' represents neighbors of device
            for device_id, neighbors in item.items():
                if device_id in self.visited:
                    print("This should not happen!")
                else:
                    self.visited.append(device_id)
                    self.logger.debug(msg="Device {} has been visited.".format(device_id))
                self.logger.info(msg="Processing {} neighbor(s) of device {}".format(len(neighbors), device_id))
                #self.data[device_id] = neighbors
                for neighbor in self.discover_filter.universal_cleanup(data=neighbors):
                    neighbor_id = self._gen_device_id(ip= neighbor["ipAddress"], hostname=neighbor["hostname"])
                    if neighbor_id in self.visited:
                        self.logger.info(msg="Neighbor {} of device {} has already been visited.".format(neighbor_id, device_id))
                        continue
                    elif neighbor_id in self.discovered:
                        self.logger.info(msg="Neighbor {} of device {} has already been discovered, waiting to be visited.".format(neighbor_id, device_id))
                        continue
                    else:
                        self.logger.info(msg="Discovered new neighbor {} of device {}.".format(neighbor_id, device_id))
                        self.discovered.append(neighbor_id)
                        self.to_visit.append({neighbor_id: {"ip": neighbor["ipAddress"], "hostname": neighbor["hostname"]}})
                        self.queue.put({"ip": neighbor["ipAddress"], "hostname": neighbor["hostname"]})
        self.to_process = []
        self.logger.info(msg="All outputs of current round have been processed. Time: {} seconds.".format(timeit.default_timer() - start_time))

    def worker(self):
        """
        This is a wrapper function that is run as thread.

        :return: ``None``
        """
        self.logger.debug(msg="Thread {} started.".format(threading.current_thread().getName()))
        if self.queue.empty():
            self.logger.debug(msg="No work for thread {}.".format(threading.current_thread().getName()))
        while not self.queue.empty():
            params = self.queue.get()
            if params is None:
                break
            self.get_neighbors(**params)
            self.queue.task_done()

    def run(self, ip):
        """
        This function starts the discovery process based on given IP address of the `seed` device.

        :param str ip: IP address of the seed device
        :return: ``None``
        """
        self.get_neighbors(ip=ip)
        self.process_neighbors()
        while len(self.to_visit) > 0:
            self.current_depth += 1
            self.logger.info("Current Discovery Depth: {} (Max: {})".format(self.current_depth, self.max_depth))
            if self.current_depth > self.max_depth:
                self.logger.info("Stopping Discovery, Max Depth Exceeded")
                break
            current_hosts = [list(x.keys())[0] for x in self.to_visit]
            self.logger.info("Nodes to be visited in this round: {}".format(current_hosts))
            try:
                for i in range(min([self.workers, len(self.to_visit)])):
                    t = threading.Thread(name="DiscoveryThread-{}".format(i), target=self.worker)
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

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "{}-{}".format(ip, timestamp)
        write_output(path="discovery", filename=filename, data=self.data, logger=self.logger)
        self.topology = CliTopology()
        self.topology.build_topology(self.data)
        filename = "{}_topology-{}".format(ip, timestamp)
        write_output(path="discovery", filename=filename, data=self.topology.topology, logger=self.logger)

