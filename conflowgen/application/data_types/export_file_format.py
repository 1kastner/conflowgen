import enum


class ExportFileFormat(enum.Enum):
    """
    The export file format supports tables. The export function enables the user to read in the generated synthetic data
    into another tool, such as a software for mathematical optimization or discrete event simulation.
    """
    csv = "csv"
    xlsx = "xlsx"
    xls = "xls"
