from nuaal.connections.api.ciscoapi import CiscoApiBase
from nuaal.utils import get_logger
import json
from urllib.parse import quote
import timeit
from nuaal.definitions import DATA_PATH
from copy import deepcopy

class CiscoEoxApi(CiscoApiBase):
    def __init__(self, usernaeme=None, password=None, api_user_id=None, DEBUG=False):
        super(CiscoEoxApi, self).__init__(username=usernaeme,
                                          password=password,
                                          api_user_id=api_user_id,
                                          api_base_path="/supporttools/eox/rest/5",
                                          con_type="CiscoEoxApi",
                                          DEBUG=DEBUG
                                          )

    def process_response(self, response):
        eox_records = {}
        for eox_record in response:
            pass
        pass

    def eox_by_pn(self, pn):
        start = timeit.default_timer()
        data = []
        if isinstance(pn, str):
            pn = [x.strip() for x in pn.split(",")]
        self.logger.debug(msg="Getting EoX information for {} PNs".format(len(pn)))
        if len(pn) <= 20:
            pn_str = ",".join(pn)
            response = self.get(path="/{}/{}".format("EOXByProductID", pn_str))
            data += response["EOXRecord"]
        else:
            response = self.get_threaded(path="/EOXByProductID", queries=pn, workers=2, max_query_len=20)
            for x in response:
                data += x["EOXRecord"]
            print(len(data))
        end = timeit.default_timer()
        self.logger.debug(msg="Fetching {} PNs took {} seconds.".format(len(pn), end-start))
        return data

    def eox_by_sn(self, sn):
        eox_records = []
        if isinstance(sn, str):
            sn = [x.strip() for x in sn.split(",")]
        chunks = [sn[x:x + 20] for x in range(0, len(sn), 20)]
        for chunk in chunks:
            chunk = ",".join(chunk)
            response = self.get(path="/{}/{}".format("EOXBySerialNumber", chunk))
            eox_records += response["EOXRecord"]
        return eox_records

    def eox_by_date(self, start_date, end_date):
        response = self.get(path="/{}/{}/{}".format("EOXByDates", start_date, end_date))
        return response["EOXRecord"]

    def check_record(self, record):
        result = {"has_eox": None, "migration_pid": None, "is_wildcard": None}
        if record["EOLProductID"] == "":
            result["has_eox"] = False
            result["migration_pid"] = False
        else:
            result["has_eox"] = record["EOLProductID"]
            if record["EOXMigrationDetails"]["MigrationProductId"] == "":
                result["migration_pid"] = False
            else:
                result["migration_pid"] = record["EOXMigrationDetails"]["MigrationProductId"]
        if "*" in record["EOXInputValue"]:
            result["is_wildcard"] = True
        else:
            result["is_wildcard"] = False

        return result

    def process_response(self, eox_records, recursive=False):
        date_fields = ["EOXExternalAnnouncementDate", "EndOfSaleDate", "EndOfSWMaintenanceReleases", "EndOfRoutineFailureAnalysisDate",
                       "EndOfServiceContractRenewal", "LastDateOfSupport", "EndOfSvcAttachDate", "UpdatedTimeStamp"]
        structure = {
            "EOLProductID": "",
            "ProductIDDescription": "",
            "ProductBulletinNumber": "",
            "LinkToProductBulletinURL": "",
            "EOXExternalAnnouncementDate": "",
            "EndOfSaleDate": "",
            "EndOfSWMaintenanceReleases": "",
            "EndOfRoutineFailureAnalysisDate": "",
            "EndOfServiceContractRenewal": "",
            "LastDateOfSupport": "",
            "EndOfSvcAttachDate": "",
            "UpdatedTimeStamp": "",
            "EOXMigrationDetails": {}
        }
        migration_details = {
            "PIDActiveFlag": "",
            "MigrationInformation": "",
            "MigrationOption": "",
            "MigrationProductId": "",
            "MigrationProductName": "",
            "MigrationStrategy": "",
            "MigrationProductInfoURL": "",
            "PIDStatus": "Unknown"
            }

        new_records = {}
        for eox_record in eox_records:
            result = self.check_record(eox_record)
            if result["has_eox"]:
                self.logger.debug(msg="Found EoX info for PN: {}".format(result["has_eox"]))
                pid = result["has_eox"]
                if pid not in new_records.keys():
                    new_record = deepcopy(structure)
                    for key in structure.keys():
                        if isinstance(eox_record[key], str):
                            new_record[key] = eox_record[key]
                        elif key in date_fields:
                            new_record[key] = eox_record[key]["value"]
                        else:
                            pass
                    new_records[pid] = new_record
                if result["migration_pid"]:
                    new_migration = deepcopy(migration_details)
                    for key, value in eox_record["EOXMigrationDetails"].items():
                        new_migration[key] = value
                    if result["migration_pid"] not in new_records[pid]["EOXMigrationDetails"].keys():
                        new_records[pid]["EOXMigrationDetails"][result["migration_pid"]] = new_migration
                print(new_record)
            else:
                self.logger.debug(msg="No EoX records found for query: {} : {}".format(eox_record["EOXInputType"], eox_record["EOXInputValue"]))
                if not result["is_wildcard"]:
                    pass
                    # TODO: Continue here
        return new_records

    def recursive_check(self, eox_records):
        pids_to_check = []
        while True:
            eox_pids = list(eox_records.keys())
            for pid, record in eox_records.items():
                for migration_pid, migration_record in record["EOXMigrationDetails"].items():
                    if migration_record["PIDStatus"] == "Unknown":
                        if migration_pid not in eox_records.keys():
                            pids_to_check.append(migration_pid)
                        else:
                            migration_record["PIDStatus"] = "FoundEoX"
            print(pids_to_check)
            if len(pids_to_check) == 0:
                break
            eox_records.update(self.process_response(self.eox_by_pn(pn=pids_to_check)))
            pids_to_check = []







if __name__ == '__main__':
    eoxapi = CiscoEoxApi(api_user_id="ad", DEBUG=True)
    eoxapi._initialize()
    short = ["WS-C3850-24T-L"]
    long = ["WS-C3560G-48PS-S", "WS-C3850-24T-L","WS-C3850-48T-L","WS-C3850-24P-L","WS-C3850-24U-L","WS-C3850-48P-L","WS-C3850-48F-L","WS-C3850-48U-L","WS-C3850-24T-S","WS-C3850-48T-S","WS-C3850-24P-S","WS-C3850-24U-S","WS-C3850-48P-S","WS-C3850-48F-S","WS-C3850-48U-S","WS-C3850-24T-E","WS-C3850-48T-E","WS-C3850-24P-E","WS-C3850-24U-E","WS-C3850-48P-E","WS-C3850-48F-E","WS-C3850-48U-E","WS-C3850-12X48U-L","WS-C3850-12X48U-S","WS-C3850-12X48U-E","WS-C3850-24XU-L","WS-C3850-24XU-S","WS-C3850-24XU-E","WS-C3850-12S-S","WS-C3850-12S-E","WS-C3850-24S-S","WS-C3850-24S-E","WS-C3850-12XS-S","WS-C3850-12XS-E","WS-C3850-24XS-S","WS-C3850-24XS-E","WS-C3850-48XS-S","WS-C3850-48XS-E","WS-C3850-48XS-F-S","WS-C3850-48XS-F-E"]
    #with open("{}/{}".format(DATA_PATH, "eox_test.json"), mode="w") as f:
        #json.dump(obj=eoxapi.eox_by_pn(long), fp=f, indent=2)
    #print(json.dumps(eoxapi.eox_by_pn(long), indent=2))
    eox_records = None
    with open("{}/{}".format(DATA_PATH, "eox_test.json"), mode="r") as f:
        eox_records = json.load(f)
    eox_records = eoxapi.process_response(eox_records=eox_records)
    eoxapi.recursive_check(eox_records)