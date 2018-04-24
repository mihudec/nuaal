from nuaal.utils import get_logger
from nuaal.connections.cli import Cisco_IOS_Cli
import queue
import threading
import time

class CliMultiRunner(object):

    def __init__(self, provider, ips, workers=4, DEBUG=False):
        self.provider = provider
        self.ips = ips
        self.workers = workers
        self.DEBUG = DEBUG
        self.logger = get_logger(name="CliMultiRunner", DEBUG=self.DEBUG)
        self.queue = queue.Queue()
        self.threads = []
        self.data = []

    def fill_queue(self):
        for i in range(len(self.ips)):
            provider = dict(self.provider)
            provider["ip"] = self.ips[i]
            self.queue.put(provider)

    def worker(self):
        self.logger.info(msg="Spawned new worker in {}".format(threading.current_thread()))
        while not self.queue.empty():
            provider = self.queue.get()
            if provider is None:
                break
            with Cisco_IOS_Cli(**provider) as device:
                device.get_inventory()
                device.get_license()
                device.get_version()
                device.get_config()
                self.data.append(device.data)
            self.queue.task_done()

    def thread_factory(self):
        for i in range(self.workers):
            t = threading.Thread(name="WorkerThread-{}".format(i), target=self.worker, args=())
            self.threads.append(t)

    def run(self):
        self.fill_queue()
        self.thread_factory()
        [t.start() for t in self.threads]
        self.queue.join()
