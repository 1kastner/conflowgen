# ConFlowGen Excel Interface

For convenience, ConFlowGen come shipped with an Excel interface.
This allows to create an Excel file with all input data to be easily manually modified without the use of the API.
Once ConFlowGen is installed, the command `conflowgen_excel_interface` is available on your command line.
It comes with its own help function:

```
$ conflowgen_excel_interface
usage: ConFlowGen Excel Interface [-h] [--overwrite] {create_input_excel,create_container_flow} filepath
ConFlowGen Excel Interface: error: the following arguments are required: action, filepath
```

A short explanation of the commands:
- The command `create_input_excel` creates an Excel workbook based on the current default distributions.
- The command `create_container_flow` reads in an Excel workbook and creates synthetic container book data.
  The result is stored in an SQLite file right next to the Excel workbook, using the same file name but a
  suitable file extension.

The Excel sheet in this folder has been created by running:

```
$ conflowgen_excel_interface create_container_flow ExcelInterface.xlsx
```
