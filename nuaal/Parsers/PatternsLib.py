import re


class Patterns:
    """
    This class holds all the necessary regex patterns, which are used by `ParserModule`. This class returns compiled regex patterns based on specified device
    type.
    """
    def __init__(self, device_type, DEBUG=False):
        """

        :param str device_type: String representation of device type, such as `cisco_ios`
        :param bool DEBUG: Enables/disables debugging output
        """
        self.device_type = device_type
        self.DEBUG = DEBUG
        self.map = {
            "cisco_ios": self.cisco_ios_patterns()
        }

    def get_patterns(self):
        """
        Function used for retrieving compiled regex patterns.
        :return: Dictionary of compiled regex patterns
        """
        return self.map[self.device_type]

    def cisco_ios_patterns(self):
        """
        This function holds regex patterns for `cisco_ios` device type.
        :return:
        """
        patterns = {
            "level0": {
                "show inventory": [
                    re.compile(
                        pattern=r"^NAME:\s\"(?P<name>[\w\s()/]+)\",\s+DESCR:\s\"(?P<desc>(?:[\w\s(),.\-_+/#:&]+))\"\s*PID:\s(?P<pid>\S+)\s*,\s+VID:\s(?P<vid>\S+)?\s*,\s+SN:\s+(?P<sn>\S+)",
                        flags=re.MULTILINE
                    )
                ],
                "show vlan brief": [
                    re.compile(
                        pattern=r"^(?P<id>\d+)\s+(?P<name>\S+)\s+(?P<status>\S+)\s+(?P<access_ports>(?:[A-Za-z]+\d+(?:\/\d+){0,2},?\s+)+)?",
                        flags=re.MULTILINE
                    )
                ],
                "show interfaces": [
                    re.compile(
                        pattern=r"^\S.*(?:$\s+^\s.*)+",
                        flags=re.MULTILINE
                    )
                ],
                "show etherchannel summary": [
                    re.compile(
                        pattern="^(?P<group>\d+)\s+(?P<portchannel>Po\d{1,3})\((?P<status>[DIHRUPsSfMuwd]{1,2})\)\s+(?P<protocol>\S+)\s+(?P<ports>(?:(?:\w+\d+(?:\/\d+)*)\(\S\)\s*)+)",
                        flags=re.MULTILINE
                    )
                ],
                "show cdp neighbors detail": [
                    re.compile(
                        pattern=r"(?<=-{25}\n).*?(?=-{25}|$)",
                        flags=re.DOTALL
                    )
                ],
                "show version": [
                    re.compile(
                        pattern=r"^Cisco.*Configuration\sregister\sis\s\S+",
                        flags=re.DOTALL
                    )
                ],
                "show mac address-table": [
                    re.compile(
                        pattern=r"^\s+(?P<vlan>\S+)\s+(?P<mac>(?:[\da-f]{4}\.?){3})\s+(?P<type>\S+)\s+(?P<ports>\S+)",
                        flags=re.MULTILINE
                    ),
                    re.compile(
                        pattern=r"^(?P<mac>(?:[\da-f]{4}\.?){3})\s+(?P<type>\S+)\s+(?P<vlan>\S+)\s+(?P<ports>\S+)",
                        flags=re.MULTILINE
                    )
                ],
                "show ip arp": [
                    re.compile(
                        pattern=r"^(?P<protocol>\S+)\s+(?P<ipAddress>((?:\d{1,3}.?){4}))\s+(?P<age>(?:\d+|-))\s+(?P<mac>(?:[\da-f]{4}\.?){3})\s+(?P<type>\S+)\s+(?P<interface>\S+)",
                        flags=re.MULTILINE
                    )
                ],
                "show license": [
                    re.compile(
                        pattern=r"^Index.*(?:(?:$\s+^\s.*)+)?",
                        flags=re.MULTILINE
                    )
                ]
            },
            "level1": {
                "show vlan brief": {
                    "access_ports": [
                        re.compile(
                            pattern=r"[A-Za-z]+\d+(?:\/\d+){0,2}"
                        )
                    ]
                },
                "show version": {
                    "version": [
                        re.compile(
                            pattern=r"^(?P<vendor>[Cc]isco)\s(?P<software>IOS(?:\sXE)?)\sSoftware,.*Version\s(?P<version>\S+)(?:,)?",
                            flags=re.MULTILINE
                        ),
                        re.compile(
                            pattern=r"^(?P<vendor>[Cc]isco)\s(?P<platform>[\w-]+).*with\s(?P<systemMemory>\d+K/\d+K)\sbytes\sof\smemory.",
                            flags=re.MULTILINE
                        ),
                        re.compile(
                            pattern=r"^$\s^(?P<hostname>[\w\-_]+)\suptime\sis\s(?P<uptime>.*)$",
                            flags=re.MULTILINE
                        ),
                        re.compile(
                            pattern=r"^System\simage\sfile\sis\s\"(?P<imageFile>.*)\"",
                            flags=re.MULTILINE
                        ),
                        re.compile(
                            pattern=r"Experimental\sVersion\s(?P<experimental_version>\S+)",
                            flags=re.MULTILINE
                        )
                    ]
                },
                "show interfaces": {
                    "name": [
                        re.compile(
                            pattern=r"^(?P<name>\S+)\sis\s(?P<status>.*),\sline\sprotocol\sis\s(?P<lineProtocol>\S+)",
                            flags=re.MULTILINE
                        ),
                        re.compile(
                            pattern=r"^(?P<name>\S+)",
                            flags=re.MULTILINE
                        )
                    ],
                    "address": [
                        re.compile(
                            pattern=r"^\s+Hardware\sis\s(?P<hardware>.*),\saddress\sis\s(?P<mac>\S+)\s\(bia\s(?P<bia>\S+)\)",
                            flags=re.MULTILINE
                        )
                    ],
                    "description": [
                        re.compile(
                            pattern=r"^\s+Description:\s(?P<description>.*)",
                            flags=re.MULTILINE
                        )
                    ],
                    "ipv4Address": [
                        re.compile(
                            pattern=r"^\s+Internet\saddress\sis\s(?P<ipv4Address>[\d\.]+)\/(?P<ipv4Mask>\d+)",
                            flags=re.MULTILINE
                        )
                    ],
                    "rates": [
                        re.compile(
                            pattern=r"^\s+(?P<loadInterval>\d+\s\S+)\sinput\srate\s(?P<inputRate>\d+).*,\s(?P<inputPacketsInterval>\d+).*$"
                                                 r"\s+.*output\srate\s(?P<outputRate>\d+).*,\s(?P<outputPacketsInterval>\d+)",
                            flags=re.MULTILINE
                        )
                    ],
                    "duplex": [
                        re.compile(
                            pattern=r"^\s+(?P<duplex>\S+)-duplex,\s(?P<speed>(?:\d+)?\S+)(?:,\s+link\stype\sis\s(?P<linkType>\S+))?,\smedia\stype\sis\s(?P<mediaType>.*)",
                            flags=re.MULTILINE
                        ),
                        re.compile(
                            pattern=r"^\s+(?P<duplex>\S+)-duplex,\s(?P<sped>\S+)$",
                            flags=re.MULTILINE
                        )
                    ],
                    "mtu": [re.compile(pattern=r"^\s+MTU\s(?P<mtu>\d+).*BW\s(?P<bandwidth>\d+)\sKbit(?:/sec)?,\sDLY\s(?P<delay>\d+).*$"
                                               r"\s+reliability\s(?P<reliability>\S+),\stxload\s(?P<txLoad>\S+),\srxload\s(?P<rxLoad>\S+)",
                                       flags=re.MULTILINE),
                            ],
                    "pseudowire": [
                        re.compile(
                            pattern=r"^\s+Encapsulation\s(?P<encapsulation>\w+)",
                            flags=re.MULTILINE
                        ),
                        re.compile(
                            pattern=r"^\s+RX\s+(?P<rxPackets>\d+)\spackets\s(?P<rxBytes>\d+)\sbytes\s(?P<rxDrops>\d+)\sdrops\s+TX\s+(?P<txPackets>\d+)\spackets\s(?P<txBytes>\d+)\sbytes\s(?P<txDrops>\d+)\sdrops",
                            flags=re.MULTILINE
                        ),
                        re.compile(
                            pattern=r"^\s+Peer\sIP\s(?P<peerIP>[\d\.]+),\sVC\sID\s(?P<virtualCircuitID>\d+)",
                            flags=re.MULTILINE
                        ),
                        re.compile(
                            pattern=r"^\s+MTU\s(?P<mtu>\d+)\sbytes",
                            flags=re.MULTILINE
                        )
                    ],
                    "input_counters": [
                        re.compile(pattern=r"^\s+(?P<rxPackets>\d+)\spackets\sinput,\s(?P<rxBytes>\d+)\sbytes,\s(?P<noBuffer>\d+)\sno\sbuffer$",
                                   flags=re.MULTILINE),
                        re.compile(pattern=r"\s+Received\s(?P<rxBroadcasts>\d+).*\((?P<rxMulticasts>\d+).*$",
                                   flags=re.MULTILINE),
                        re.compile(pattern=r"\s+(?P<runts>\d+)\srunts,\s(?P<giants>\d+)\sgiants,\s(?P<throttles>\d+).*$",
                                   flags=re.MULTILINE),
                        re.compile(pattern=r"\s+(?P<inputErrors>\d+)\sinput\serrors,\s(?P<crc>\d+)\sCRC,\s(?P<frame>\d)\sframe,\s(?P<overrun>\d+)\soverrun,\s(?P<ignored>\d+).*$",
                                   flags=re.MULTILINE),
                        re.compile(pattern=r"(?:\s+(?P<watchdog>\d+)\swatchdog,\s(?P<multicasts>\d+)\smulticast,\s(?P<pauseInput>\d+)\spause\sinput$\s+(?P<inputPacketsWithDribbleCondition>\d+)\sinput.*)?",
                                   flags=re.MULTILINE)
                    ],
                    "output_counters": [
                        re.compile(pattern=r"^\s+(?P<txPackets>\d+)\spackets\soutput,\s(?P<txBytes>\d+)\sbytes,\s(?P<underruns>\d+)\sunderruns$",
                                   flags=re.MULTILINE),
                        re.compile(pattern=r"\s+(?P<outputErrors>\d+)\soutput\serrors,\s(?:(?P<collision>\d+)\scollisions,\s)?(?P<interfaceResets>\d+)\sinterface\sresets$",
                                   flags=re.MULTILINE),
                        re.compile(pattern=r"\s+(?P<babbles>\d+)\sbabbles,\s(?P<lateCollision>\d+)\slate\scollision,\s(?P<deferred>\d+)\sdeferred$",
                                   flags=re.MULTILINE),
                        re.compile(pattern=r"\s+(?P<lostCarrier>\d+)\slost\scarrier,\s(?P<noCarrier>\d+)\sno\scarrier,\s(?P<pauseOutput>\d+)\sPAUSE\soutput$",
                                   flags=re.MULTILINE),
                        re.compile(pattern=r"\s+(?P<outputBufferFailures>\d+)\soutput\sbuffer\sfailures,\s(?P<outputBufferSwappedOut>\d+)\soutput buffers swapped out$",
                                   flags=re.MULTILINE)
                    ]
                },
                "show etherchannel summary": {
                    "ports": [
                        re.compile(
                            pattern=r"(?P<port>\w+\d+(?:\/\d+)*)\((?P<status>[A-Za-z]+)\)"
                        )
                    ]
                },
                "show cdp neighbors detail": {
                    "hostname": [
                        re.compile(pattern=r"^Device\sID:\s(?P<hostname>[\w\_\-\(\)]+)(?:.\S+)?", flags=re.MULTILINE),
                        re.compile(pattern=r"^Device\sID:\s(?P<hostname>\S+)", flags=re.MULTILINE)
                    ],
                    "ipAddress": [re.compile(pattern=r"IP\saddress:\s(?P<ipAddress>(?:\d{1,3}\.?){4})", flags=re.MULTILINE)],
                    "platform": [re.compile(pattern=r"^Platform:\s(?:(?:Cisco|cisco\s)?(?P<platform>(?:\S+\s?)+))", flags=re.MULTILINE)],
                    "capabilities": [re.compile(pattern=r"Capabilities:\s(?P<capabilities>(?:\S+\s)+)")],
                    "localInterface": [re.compile(pattern=r"^Interface:\s(?P<localInterface>[A-Za-z]+\d+(?:\/\d+)*)", flags=re.MULTILINE)],
                    "remoteInterface": [re.compile(pattern=r"Port\sID\s\(outgoing\sport\):\s(?P<remoteInterface>[A-Za-z]+\d+(?:\/\d+)*)")]
                },
                "show license": {
                    "index": [re.compile(pattern=r"^Index\s(?P<index>\d+)")],
                    "feature": [re.compile(pattern=r"Feature:\s(?P<feature>\S+)")],
                    "period_left": [re.compile(pattern=r"Period\sleft:\s(?P<period_left>.*)")],
                    "period_used": [re.compile(pattern=r"Period\sUsed:\s(?P<period_used>.*)")],
                    "license_type": [re.compile(pattern=r"License\sType:\s(?P<license_type>.*)")],
                    "license_state": [re.compile(pattern=r"License\sState:\s(?P<license_state>.*)")],
                    "license_count": [re.compile(pattern=r"License\sCount:\s(?P<license_count>.*)")],
                    "license_priority": [re.compile(pattern=r"License\sPriority:\s(?P<license_priority>.*)")],
                }
            }
        }
        return patterns
