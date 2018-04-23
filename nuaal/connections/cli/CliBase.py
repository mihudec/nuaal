from netmiko import ConnectHandler
from netmiko.ssh_exception import *
import json
from nuaal.utils import get_logger, check_path
from nuaal.utils import Filter
from nuaal.definitions import DATA_PATH
import timeit

class CliBaseConnection(object):
    def __init__(self, ip=None, username=None, password=None, parser=None, secret=None, enable=False, store_outputs=False, DEBUG=False):
        self.ip = ip
        self.username = username
        self.password = password
        self.ssh_method = None
        self.telnet_method = None
        self.primary_method = None
        self.secondary_method = None
        self.secret = secret
        self.enable = enable
        self.provider = None
        self._get_provider()
        self.store_outputs = store_outputs
        self.enabled = None
        self.prompt_end = [">", "#"] # The first item is for 'not-enabled mode', the second is for 'Privileged EXEC Mode'
        self.logger = get_logger(f"Connection-{self.ip}", DEBUG=DEBUG)
        self.parser = parser
        self.connected = False

        self.outputs = {}
        self.data = {"ipAddress": self.ip}
        self.device = None

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.store_raw_output(f"{self.data['hostname']}", json.dumps(self.data, indent=2), ext="json")
        self.disconnect()

    def _get_provider(self):
        self.provider = {
            "ip": self.ip,
            "username": self.username,
            "password": self.password
        }
        if self.secret:
            self.provider["secret"] = self.secret

    def _connect_telnet(self):
        device = None
        self.provider["device_type"] = self.telnet_method
        self.logger.debug(msg=f"Trying to connect to device {self.ip} via Telnet...")
        try:
            device = ConnectHandler(**self.provider)
        except TimeoutError:
            self.logger.error(msg=f"Could not connect to '{self.ip}' using '{self.telnet_method}'. Reason: TimeOut.")
        except ConnectionRefusedError:
            self.logger.error(msg=f"Could not connect to '{self.ip}' using '{self.telnet_method}'. Reason: Connection Refused.")
        except Exception as e:
            print(repr(e))
            self.logger.error(msg=f"Could not connect to '{self.ip}' using '{self.telnet_method}'. Reason: Unknown.")
        finally:
            if device:
                self.logger.info(msg=f"Connected to '{self.ip}' using '{self.telnet_method}'.")
            return device

    def _connect_ssh(self):
        device = None
        self.logger.debug(msg=f"Trying to connect to device {self.ip} via SSH...")
        self.provider["device_type"] = self.ssh_method
        try:
            device = ConnectHandler(**self.provider)
        except NetMikoTimeoutException:
            self.logger.error(msg=f"Could not connect to '{self.ip}' using '{self.ssh_method}'. Reason: Timeout.")
        except NetMikoAuthenticationException:
            self.logger.error(msg=f"Could not connect to '{self.ip}' using '{self.ssh_method}'. Reason: Authentication Failed.")
        except Exception as e:
            print(repr(e))
            self.logger.error(msg=f"Could not connect to '{self.ip}' using '{self.ssh_method}'. Reason: Unknown.")
        finally:
            if device:
                self.logger.info(msg=f"Connected to '{self.ip}' using '{self.ssh_method}'.")
            return device

    def _connect(self):
        device = None

        if self.primary_method == self.ssh_method:
            device = self._connect_ssh()
        elif self.primary_method == self.telnet_method:
            device = self._connect_telnet()
        if not device:
            if self.secondary_method == self.telnet_method:
                device = self._connect_telnet()
            elif self.secondary_method == self.ssh_method:
                self._connect_ssh()

        if device is not None:
            self._check_enable_level(device)
        else:
            self.logger.error(msg=f"Could not connect to device '{self.ip}'")

    def _check_enable_level(self, device):
        try:
            prompt = device.find_prompt()
            self.data["hostname"] = prompt[:-1]
            if prompt[-1] == self.prompt_end[0]:
                self.enabled = False
            if prompt[-1] == self.prompt_end[1]:
                self.enabled = True
            if self.enable and not self.enabled:
                device.enable()
                if device.find_prompt()[-1] == self.prompt_end[1]:
                    self.logger.debug(msg=f"Successfully enabled Privileged EXEC Mode on device '{self.ip}'")
                    self.enabled = True
                else:
                    self.logger.error(msg=f"Failed to enable Privileged EXEC Mode on device '{self.ip}'")
            if not self.enable and self.enabled:
                device.exit_enable_mode()
                if device.find_prompt()[-1] ==self.prompt_end[0]:
                    self.logger.debug(msg=f"Successfully disabled Privileged EXEC Mode on device '{self.ip}'")
                    self.enabled = True
                else:
                    self.logger.error(msg=f"Failed to disable Privileged EXEC Mode on device '{self.ip}'")
        except ValueError as e:
            self.logger.critical(msg=f"Could not enter enable mode: {repr(e)}")
        except Exception as e:
            print(repr(e))
        finally:
            self.device = device

    def disconnect(self):
        if self.device is not None:
            self.device.disconnect()
            if not self.device.is_alive():
                self.logger.info(msg=f"Successfully disconnected from device {self.ip}")
            else:
                self.logger.error(msg=f"Failed to disconnect from device {self.ip}")
        else:
            self.logger.info(msg=f"Device {self.ip} is not connected.")

    def _send_command(self, command):
        if not self.device:
            self.logger.error(msg=f"Device {self.ip} is not connected, cannot send command.")
            return None
        self.logger.debug(msg=f"Sending command '{command}' to device {self.data['hostname']} ({self.ip})")
        output = ""
        try:
            output = self.device.send_command_expect(command)
        except AttributeError:
            self.logger.critical(msg=f"Connection to device {self.ip} has not been initialized.")
        finally:
            return output

    def _send_commands(self, commands):
        output = {}
        for command in commands:
            output[command] = self._send_command(command)
        return output

    def _command_handler(self, action, filter=None):
        """
        This function tries to send multiple 'types' of given command and waits for correct output.
        This should solve the problem with different command syntax, such as 'show mac address-table' vs
        'show mac-address-table' on different versions of Cisco IOS.
        When correct output is returned, it is then parsed and the result is returned
        :param commands: List of command string to try, such as ['show mac-address-table', 'show mac address-table']
        :return: JSON representation of command output
        """
        start_time = timeit.default_timer()
        commands = self.command_mappings[action]
        command_output = ""
        used_command = ""
        parsed_output = []
        for command in commands:
            command_output = self._send_command(command)
            if not command_output:
                self.logger.error(msg=f"Could not retrieve any output. Possibly non-active connection.")
                return []
            #print(f"Command '{command}' returned output: \n'{command_output}'")
            if "% Invalid input detected at '^' marker." in command_output:
                self.logger.error(msg=f"Device {self.ip} does not support command '{command}'")
            elif "% Ambiguous command:" in command_output:
                self.logger.error(msg=f"Device {self.ip}: Ambiguous command: '{command}'")
            elif command_output == "":
                self.logger.error(msg=f"Device {self.ip} returned empty output for command '{command}'")
            else:
                self.logger.debug(msg=f"Device {self.ip} returned output for command '{command}'")
                used_command = command
                break
        if self.store_outputs and command_output != "":
            self.store_raw_output(command=used_command, raw_output=command_output)
        if command_output == "":
            return []
        # Try parsing the output
        try:
            parsed_output = self.parser.autoparse(command=commands[0], text=command_output)
            if isinstance(filter, Filter):
                parsed_output = filter.universal_cleanup(data=parsed_output)
            self.data[action[4:]] = parsed_output
        except Exception as e:
            print(repr(e))
            self.logger.error(msg=f"Device {self.ip}: Failed to parse output of command '{used_command}'")
        finally:
            self.logger.debug(msg=f"Processing of action {action} took {timeit.default_timer()-start_time} seconds.")
            return parsed_output

    def store_raw_output(self, command, raw_output, ext="txt"):
        path = f"{DATA_PATH}/outputs/{self.ip}"
        path = check_path(path)
        if path:
            with open(f"{path}/{command}.{ext}", mode="w+") as f:
                f.write(raw_output)

    #####################
    ### GET Functions ###
    #####################

    def get_vlans(self):
        return self._command_handler(action="get_vlans")

    def get_inventory(self):
        return self._command_handler(action="get_inventory")

    def get_interfaces(self):
        return self._command_handler(action="get_interfaces")

    def get_portchannels(self):
        return self._command_handler(action="get_portchannels")

    def get_license(self):
        return self._command_handler(action="get_license")

    def get_version(self):
        return self._command_handler(action="get_version")

    def get_mac_address_table(self):
        return self._command_handler(action="get_mac_address_table")

    def get_arp(self):
        return self._command_handler(action="get_arp")

    def __str__(self):
        return f"[Connection -> {self.ip}]"

    def __repr__(self):
        return f"[Connection -> {self.ip}]"