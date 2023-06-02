import enum

import enum_tools


@enum_tools.documentation.document_enum
class ExportFileFormat(enum.Enum):
    """
    The export file format supports tables.
    The export function enables the user to read in the generated synthetic data into another tool, such as a software
    for mathematical optimization or discrete event simulation.
    """

    csv = "csv"
    """
    Comma-separated values files are very simplistic representation but unrestricted and widely supported.
    """

    xlsx = "xlsx"
    """
    The xlsx file format can be opened by, e.g., Microsoft Excel which might help to quickly analyse the output data.
    However, this file format comes with known limitations listed at
    https://support.microsoft.com/en-us/office/excel-specifications-and-limits-1672b34d-7043-467e-8e27-269d656771c3.
    On January 4th, 2022, the known maximum number of rows is 1,048,576.
    Thus, if, e.g., 1.1 million containers are generated, opening this xlsx file in Excel is not supported by the
    specifications.
    """

    xls = "xls"
    """
    The xls format is the precursor of the xlsx format.
    This should only be used if a software demands this file format.
    Older versions of Excel had more restrictions on the size, e.g. Excel 2003 is known to have only supported 65,536
    rows (see, e.g.,
    http://web.archive.org/web/20140819001409/http://news.office-watch.com/t/n.aspx?articleid=1408&zoneid=9)
    which is less than what large terminals nowadays handle within a month. Even with a hypothetical TEU factor of 2,
    this only reaches 1,572,864 TEU throughput per year.
    """
