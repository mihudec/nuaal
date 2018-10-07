import json
import datetime

class CiscoApiModel(object):
    def __init__(self):
        pass

    def str_to_datetime(self, date_str, date_format="%Y-%m-%d"):
        return datetime.datetime.strptime(date_str, date_format)

class EoxModel(CiscoApiModel):
    def __init__(self, eox_record):
        self.all_keys = ["EOLProductID", "ProductIDDescription", "EOXExternalAnnouncementDate", "EndOfSaleDate", "EndOfSWMaintenanceReleases", "EndOfSecurityVulSupportDate", "EndOfRoutineFailureAnalysisDate", "EndOfServiceContractRenewal", "EndOfServiceContractRenewal", "LastDateOfSupport", "EndOfSvcAttachDate", "UpdatedTimeStamp"]
        self.eox_record = eox_record if isinstance(eox_record, dict) else json.loads(eox_record)
        self.EOLProductID = self.eox_record["EOLProductID"]
        self.ProductIDDescription = self.eox_record["ProductIDDescription"]
        self.ProductBulletinNumber = self.eox_record["ProductBulletinNumber"]
        self.LinkToProductBulletinURL = self.eox_record["LinkToProductBulletinURL"]
        self.EOXExternalAnnouncementDate = self.str_to_datetime(self.eox_record["EOXExternalAnnouncementDate"]["value"])
        self.EndOfSaleDate = self.str_to_datetime(self.eox_record["EndOfSaleDate"]["value"])
        self.EndOfSWMaintenanceReleases = self.str_to_datetime(self.eox_record["EndOfSWMaintenanceReleases"]["value"])
        self.EndOfSecurityVulSupportDate = self.str_to_datetime(self.eox_record["EndOfSecurityVulSupportDate"]["value"])
        self.EndOfRoutineFailureAnalysisDate = self.str_to_datetime(self.eox_record["EndOfRoutineFailureAnalysisDate"]["value"])
        self.EndOfServiceContractRenewal = self.str_to_datetime(self.eox_record["EndOfServiceContractRenewal"]["value"])
        self.LastDateOfSupport = self.str_to_datetime(self.eox_record["LastDateOfSupport"]["value"])
        self.EndOfSvcAttachDate = self.str_to_datetime(self.eox_record["EndOfSvcAttachDate"]["value"])
        self.UpdatedTimeStamp = self.str_to_datetime(self.eox_record["UpdatedTimeStamp"]["value"])


if __name__ == '__main__':
    eox_dict = {
      "EOLProductID": "WS-C3560G-48PS-S",
      "ProductIDDescription": "Catalyst 3560 48 10/100/1000T PoE + 4 SFP + IPB Image",
      "ProductBulletinNumber": "EOL8044",
      "LinkToProductBulletinURL": "http://www.cisco.com/en/US/prod/collateral/switches/ps5718/ps5023/eol_c51-696372.html",
      "EOXExternalAnnouncementDate": {
        "value": "2012-01-31",
        "dateFormat": "YYYY-MM-DD"
      },
      "EndOfSaleDate": {
        "value": "2013-01-30",
        "dateFormat": "YYYY-MM-DD"
      },
      "EndOfSWMaintenanceReleases": {
        "value": "2014-01-30",
        "dateFormat": "YYYY-MM-DD"
      },
      "EndOfSecurityVulSupportDate": {
        "value": "2016-01-30",
        "dateFormat": "YYYY-MM-DD"
      },
      "EndOfRoutineFailureAnalysisDate": {
        "value": "2014-01-30",
        "dateFormat": "YYYY-MM-DD"
      },
      "EndOfServiceContractRenewal": {
        "value": "2017-04-30",
        "dateFormat": "YYYY-MM-DD"
      },
      "LastDateOfSupport": {
        "value": "2018-01-31",
        "dateFormat": "YYYY-MM-DD"
      },
      "EndOfSvcAttachDate": {
        "value": "2014-01-30",
        "dateFormat": "YYYY-MM-DD"
      },
      "UpdatedTimeStamp": {
        "value": "2013-09-18",
        "dateFormat": "YYYY-MM-DD"
      },
      "EOXMigrationDetails": {
        "PIDActiveFlag": "Y",
        "MigrationInformation": "Catalyst 3560X 48 Port PoE IP Base",
        "MigrationOption": "Enter PID(s)",
        "MigrationProductId": "WS-C3560X-48P-S",
        "MigrationProductName": "",
        "MigrationStrategy": "",
        "MigrationProductInfoURL": "http://www.cisco.com/en/US/products/ps10745/index.html and http://www.cisco.com/en/US/products/ps10744/index.html"
      },
      "EOXInputType": "ShowEOXByPids",
      "EOXInputValue": "WS-C3560G-48PS-S "
    }

    eox_entry = EoxModel(eox_dict)
    print(eox_entry.EOXExternalAnnouncementDate)