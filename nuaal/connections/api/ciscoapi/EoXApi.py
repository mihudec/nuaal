from nuaal.connections.api.ciscoapi import CiscoApiBase
import json
from copy import deepcopy


class EoxApi(CiscoApiBase):
    def __init__(self, usernaeme=None, password=None, api_user_id=None, DEBUG=False):
        super(EoxApi, self).__init__(username=usernaeme,
                                     password=password,
                                     api_user_id=api_user_id,
                                     api_base_path="/supporttools/eox/rest/5",
                                     con_type="CiscoEoxApi",
                                     DEBUG=DEBUG
                                     )
        self.data = {}
        self._initialize()

    def clear_query(self, query):
        if isinstance(query, str):
            query = [x.strip() for x in query.split(",")]
        elif isinstance(query, list):
            query = [x.strip() for x in query]
        else:
            raise TypeError("clear_query takes CSV-like string or list of strings "
                            "as argument. {} given.".format(type(query)))
        return query

    def get_by_query(self, path, query, max_queries=20, workers=2):
        raw_response = []
        try:
            query = self.clear_query(query)
        except TypeError:
            self.logger.error("Unsupported query format. Use either CSV-like string or list of srings.")
            query = []
        if len(query) <= max_queries:
            query_str = ",".join(query)
            try:
                raw_response = self.get(path="/{}/{}".format(path, query_str))["EOXRecord"]
            except Exception as e:
                self.logger.error(msg="Encountered Exception when retrieving EoX Response: {}".format(repr(e)))
                raw_response = []
            print(json.dumps(raw_response, indent=2))
        else:
            raw_response = self.get_threaded(path=path, queries=query, max_query_len=max_queries, workers=workers)
            new_response = []
            try:
                raw_response = [x["EOXRecord"] for x in raw_response]
                for page in raw_response:
                    new_response += page
                raw_response = new_response
            except Exception as e:
                self.logger.error(msg="Encountered Exception when retrieving EoX Response: {}".format(repr(e)))
                raw_response = []
            print(json.dumps(raw_response, indent=2))

        return self.process_response(query=query, raw_response=raw_response)

    def process_response(self, query, raw_response):
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
            "EOXMigrationDetails": {},
            "EOXInputType": "",
            "EOXInputValue": ""
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
        processed_records = {}
        for eox_record in raw_response:
            if eox_record["EOLProductID"] == "":
                continue
            if eox_record["EOLProductID"] not in processed_records.keys():
                new_record = deepcopy(structure)
                for key in structure:
                    if isinstance(eox_record[key], str):
                        new_record[key] = eox_record[key]
                    elif key in date_fields:
                        new_record[key] = eox_record[key]["value"]
                    else:
                        pass
                processed_records[eox_record["EOLProductID"]] = new_record
            if eox_record["EOXMigrationDetails"]["MigrationProductId"] != "":
                new_migration = deepcopy(migration_details)
                for k, v in eox_record["EOXMigrationDetails"].items():
                    new_migration[k] = v
                new_migration["PIDStatus"] = "Unknown"
                processed_records[eox_record["EOLProductID"]]["EOXMigrationDetails"][eox_record["EOXMigrationDetails"]["MigrationProductId"]] = new_migration
        return processed_records






if __name__ == '__main__':
    long = ["WS-C3560G-48PS-S", "WS-C3850-24T-L","WS-C3850-48T-L","WS-C3850-24P-L","WS-C3850-24U-L","WS-C3850-48P-L","WS-C3850-48F-L","WS-C3850-48U-L","WS-C3850-24T-S","WS-C3850-48T-S","WS-C3850-24P-S","WS-C3850-24U-S","WS-C3850-48P-S","WS-C3850-48F-S","WS-C3850-48U-S","WS-C3850-24T-E","WS-C3850-48T-E","WS-C3850-24P-E","WS-C3850-24U-E","WS-C3850-48P-E","WS-C3850-48F-E","WS-C3850-48U-E","WS-C3850-12X48U-L","WS-C3850-12X48U-S","WS-C3850-12X48U-E","WS-C3850-24XU-L","WS-C3850-24XU-S","WS-C3850-24XU-E","WS-C3850-12S-S","WS-C3850-12S-E","WS-C3850-24S-S","WS-C3850-24S-E","WS-C3850-12XS-S","WS-C3850-12XS-E","WS-C3850-24XS-S","WS-C3850-24XS-E","WS-C3850-48XS-S","WS-C3850-48XS-E","WS-C3850-48XS-F-S","WS-C3850-48XS-F-E"]
    short = ["WS-C3560G-48PS-S"]
    eoxapi = EoxApi(api_user_id="an", DEBUG=True)
    print(json.dumps(eoxapi.get_by_query(path="EOXByProductID", query=long), indent=2))
