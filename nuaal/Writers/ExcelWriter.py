from nuaal.Writers import Writer
from nuaal.utils import check_path
from nuaal.definitions import DATA_PATH
import xlsxwriter

class ExcelWriter(Writer):
    """
    This class provides functions for writing the retrieved data in Microsoft Excel format, `.xlsx`.
    """
    def __init__(self):
        super(ExcelWriter, self).__init__(type="Excel")

    def create_workbook(self, path, filename):
        """
        Function for creating Excel Workbook based on path and file name.

        :param str path: System path to Excel file
        :param str filename: Name of the Excel file.
        :return: Instance of ``xlsxwriter`` workbook object.
        """
        path = check_path(path)
        workbook = xlsxwriter.Workbook("{}/{}".format(path, filename))
        return workbook

    def write_list(self, workbook, data, worksheetname=None, headers=None):
        """
        Function for creating worksheet inside given workbook and writing provided data.

        :param workbook: Reference of the ``xlsxwriter`` workbook object.
        :param list data: List of lists, where each list represents one row in the worksheet.
        :param str worksheetname: Name of the worksheet.
        :param list headers: List of column headers.
        :return: ``None``
        """
        if isinstance(data, list):
            if worksheetname:
                self.logger.info(msg="Creating new worksheet with name {}.".format(worksheetname))
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
            self.logger.info(msg="{} entries written.".format(len(data)))

    def write_json(self, workbook, data, worksheetname=None, headers=None):
        """
        Function for writing JSON-like data to worksheet.

        :param workbook: Reference of the ``xlsxwriter`` workbook object.
        :param data:
        :param str worksheetname: Name of the worksheet
        :param list headers: List of column headers.
        :return: ``None``
        """
        if isinstance(data, list):
            if not headers:
                # Generate headers from first dict
                headers = list(data[0].keys())
            bold = workbook.add_format({"bold": True})
            # Create new worksheet
            worksheet = None
            if worksheetname:
                self.logger.info(msg="Creating new worksheet with name {}.".format(worksheetname))
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

            if headers:
                worksheet.autofilter(0, 0, row_pointer-1, len(headers)-1)

            self.logger.info(msg="{} entries writen.".format(len(data)))

        else:
            # TODO: Implement other JSON types
            self.logger.error(msg="Given JSON is not a list of dictionaries. Not yet implemented.")

    def write_data(self, workbook, data):
        """
        Function for writing entire content of device data, divided into sections based on `get_` command used.
        :param workbook: Reference of the ``xlsxwriter`` workbook object.
        :param dict data: Content of device.data variable, which holds all retrieved info.
        :return: ``None``
        """
        headers, content = self.combine_device_data(data)
        for section in headers:
            self.write_list(workbook=workbook, data=content[section], worksheetname=section, headers=headers[section])
