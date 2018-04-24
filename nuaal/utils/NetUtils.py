from nuaal.utils import get_logger
from nuaal.definitions import LOG_PATH

class IP:
    def __init__(self, ip, DEBUG=False):
        self.logger = get_logger(name="IP", logfile_path="{}/ip_log.txt".format(LOG_PATH), DEBUG=DEBUG)
        self.decAddress = None
        self.binAddress = None
        self.decMask = None
        self.binMask = None
        self.slashMask = None
        self.binNetAddress = None
        self.decNetAddress = None
        self.binBcastAddress = None
        self.decBcastAddress = None

        (addr, mask) = None, None
        if "/" in ip:
            (addr, mask) = ip.split("/")
        elif " " in ip:
            (addr, mask) = ip.split(" ")
        else:
            (addr, mask) = ip, None
        self.decAddress = addr
        self.binAddress = self.decToBin(addr)
        if mask:
            try:
                self.binMask = self.maskToBin(mask)
                self.decMask = self.binToDec(self.binMask)
                self.slashMask = self.binMask.index("0")
                self.binNetAddress = self.binAddress[:self.slashMask] + "0" * (32 - self.slashMask)
                self.binBcastAddress = self.binAddress[:self.slashMask] + "1" * (32 - self.slashMask)
                self.decNetAddress = self.binToDec(self.binNetAddress)
                self.decBcastAddress = self.binToDec(self.binBcastAddress)

            except AttributeError:
                pass

    def decToBin(self, dec):
        octects = [int(x) for x in dec.split(".")]
        # Check
        if len(octects) != 4:
            self.logger.critical(msg="Given decimal representation doesn't have correct length. Expected 4 octect, got {}".format(len(octects)))
            raise ValueError("Given decimal representation doesn't have correct length. Expected 4 octect, got {}".format(len(octects)))
        return "".join(bin(int(x) + 256)[3:] for x in dec.split("."))

    def binToDec(self, bin):
        if len(bin) != 32:
            self.logger.critical(msg="Given binary representation doesn't have correct length. Expected 24, got {}".format(len(bin)))
            raise ValueError("Given binary representation doesn't have correct length. Expected 24, got {}".format(len(bin)))
        octects = [bin[i:i + 8] for i in range(0, len(bin), 8)]
        return ".".join([str(int(x, 2)) for x in octects])

    def maskToBin(self, mask):
        # If mask is in slash notation
        try:
            mask = int(mask)
            return "1" * mask + "0" * (32 - mask)
        # If mask is in decimal notation
        except ValueError:
            mask = self.decToBin(mask)
            slashmask = mask.index("0")
            if "1" in mask[slashmask:]:
                print("Invalid netmask!")
                return None

            return mask


class IPv4Addr(IP):
    def __init__(self, address, DEBUG=False):
        super(IPv4Addr, self).__init__(ip=address, DEBUG=DEBUG)

    def __str__(self):
        return "[IPv4Addr {}/{}]".format(self.decAddress, self.slashMask)

    def __repr__(self):
        return "[IPv4Addr {}/{}]".format(self.decAddress, self.slashMask)


class IPv4Net(IP):
    def __init__(self, network, DEBUG=False):
        super(IPv4Net, self).__init__(ip=network, DEBUG=DEBUG)
        if not self.decNetAddress:
            print("No mask given!")

    def has_address(self, addr):
        if not isinstance(addr, IPv4Addr):
            self.logger.info(msg="Trying to convert {} to IPv4Addr object.".format(addr))
            try:
                addr = IPv4Addr(address=addr)
            except Exception as e:
                self.logger.critical(msg="Could not convert {} to IPv4Addr".format(type(addr)))
                raise TypeError("Could not convert {} to IPv4Addr".format(type(addr)))
        if self.binNetAddress[:self.slashMask] == addr.binAddress[:self.slashMask]:
            return True
        else:
            return False

    def has_subnet(self, addr):
        if not isinstance(addr, IPv4Net):
            self.logger.info(msg="Trying to convert {} to IPv4Addr object.".format(addr))
            try:
                addr = IPv4Net(addr)
            except Exception as e:
                self.logger.critical(msg="Could not convert {} to IPv4Net".format(type(addr)))
                raise TypeError("Could not convert {} to IPv4Net".format(type(addr)))
        if self.binNetAddress[:self.slashMask] == addr.binNetAddress[:self.slashMask]:
            return True
        else:
            return False

    def __str__(self):
        return "[IPv4Net {}/{}]".format(self.decAddress, self.slashMask)

    def __repr__(self):
        return "[IPv4Net {}/{}]".format(self.decAddress, self.slashMask)


net = IPv4Net("192.168.1.0 255.255.255.0", DEBUG=True)
print("DecAddr:", net.decAddress)
print("DecMask:", net.decMask)
print("BinAddr:", net.binAddress)
print("BinMask:", net.binMask)
print("SlashMask:", net.slashMask)
print("DecNetAddress:", net.decNetAddress)
print("binNetAddress:", net.binNetAddress)


net2 = IPv4Net("192.168.1.128 255.255.255.128", DEBUG=True)
print("DecAddr:", net2.decAddress)
print("DecMask:", net2.decMask)
print("BinAddr:", net2.binAddress)
print("BinMask:", net2.binMask)
print("SlashMask:", net2.slashMask)
print("DecNetAddress:", net2.decNetAddress)
print("binNetAddress:", net2.binNetAddress)

print(net.has_subnet(net2))
print(net2.has_subnet(net))

