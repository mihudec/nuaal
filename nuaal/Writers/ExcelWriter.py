from nuaal.Writers import Writer
from nuaal.utils import check_path
from nuaal.definitions import DATA_PATH
import xlsxwriter

class ExcelWriter(Writer):
    def __init__(self):
        super(ExcelWriter, self).__init__(type="Excel")

    def create_workbook(self, path, filename):
        path = check_path(path)
        workbook = xlsxwriter.Workbook(f"{path}/{filename}")
        return workbook

    def write_list(self, workbook, data, worksheetname=None, headers=None):
        if isinstance(data, list):
            if worksheetname:
                self.logger.info(msg=f"Creating new worksheet with name {worksheetname}.")
                worksheet = workbook.add_worksheet(name=worksheetname)
            else:
                self.logger.info(msg="Creating new worksheet.")
                worksheet = workbook.add_worksheet()
            row_pointer = 0
            column_pointer = 0
            bold = workbook.add_format({"bold": True})
            if headers:
                worksheet.write_row(row_pointer, column_pointer, headers, bold)
                row_pointer += 1
            for entry in data:
                if isinstance(entry, list):
                    worksheet.write_row(row_pointer, column_pointer, entry)
                    row_pointer += 1
            if headers:
                worksheet.autofilter(0, 0, row_pointer-1, len(data[0])-1)
            self.logger.info(msg=f"{len(data)} entries written.")

    def write_json(self, workbook, data, worksheetname=None, headers=None):
        if isinstance(data, list):
            if not headers:
                # Generate headers from first dict
                headers = list(data[0].keys())
            bold = workbook.add_format({"bold": True})
            # Create new worksheet
            worksheet = None
            if worksheetname:
                self.logger.info(msg=f"Creating new worksheet with name {worksheetname}.")
                worksheet = workbook.add_worksheet(name=worksheetname)
            else:
                self.logger.info(msg="Creating new worksheet.")
                worksheet = workbook.add_worksheet()
            row_pointer = 0
            column_pointer = 0
            worksheet.write_row(row_pointer, column_pointer, headers, bold)
            row_pointer += 1
            for entry in data:
                row = []
                # Workaround for unsupported types
                for element in [entry[x] for x in headers]:
                    if isinstance(element, list):
                        row.append(str(element))
                    else:
                        row.append(element)
                worksheet.write_row(row_pointer, column_pointer, row)
                row_pointer += 1

            self.logger.info(msg=f"{len(data)} entries writen.")

        else:
            # TODO: Implement other JSON types
            self.logger.error(msg=f"Given JSON is not a list of dictionaries. Not yet implemented.")

    def write_data(self, workbook, data):
        headers, content = self.combine_device_data(data)
        for section in headers:
            self.write_list(workbook=workbook, data=content[section], worksheetname=section, headers=headers[section])




if __name__ == '__main__':

    xls = ExcelWriter()
    workbook = xls.create_workbook(path=f"{DATA_PATH}/XLS", filename="test.xlsx")
    xls.write_json(workbook, [{"A": 1, "B": 2}])
    workbook.close()