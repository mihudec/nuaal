from nuaal.connections.api.ciscoapi import CiscoApiBase
import json


class CiscoPsirtApi(CiscoApiBase):
    def __init__(self, username=None, password=None, api_user_id=None, DEBUG=False):
        super(CiscoPsirtApi, self).__init__(username=username,
                                            password=password,
                                            api_user_id=api_user_id,
                                            api_base_path="/security/advisories",
                                            con_type="CiscoEoxApi",
                                            DEBUG=DEBUG
                                            )

    def psirt_by_sw(self, sw_type, sw_version):
        response = self.get(path="/{}".format(sw_type), params={"version": sw_version})
        return response

if __name__ == '__main__':
    psirt_client = CiscoPsirtApi(api_user_id="ad", DEBUG=True)
    psirt_client._initialize()
    psirt_client.psirt_by_sw(sw_type="ios", sw_version="15.2(1)E1")