from nuaal.connections.api.apic_em import ApicEmBase
from nuaal.utils import get_logger


class ApicEmPnpClient:
    def __init__(self, apic=None, DEBUG=False):
        """

        :param apic:
        :param DEBUG:
        """
        self.apic = apic
        self.DEBUG = DEBUG
        self.logger = get_logger(name="ApicEmPnpClient", DEBUG=self.DEBUG)
        if not isinstance(self.apic, ApicEmBase):
            self.logger.critical(msg="Given 'apic' is not an instance of 'ApicEmBase' class.")

    def template_get(self, id=None, filename=None):
        pass

