# ConFlowGen Spreadsheet Interface

For convenience, ConFlowGen come shipped with a spreadsheet interface.
This allows to create a spreadsheet file with all input data to be easily modified in
MS Excel, LibreOffice Calc, and similar
without the need to directly use the Python API.
Once ConFlowGen is installed, the command `conflowgen_spreadsheet_interface` is available on your command line.
It comes with its own help function:

```
$ conflowgen_spreadsheet_interface -h
usage: ConFlowGen Spreadsheet Interface [-h] [--overwrite] {create_input_spreadsheet,create_container_flow} filepath

The command line tool allows to create an XLSX file with all input distributions which the user can change and then read in again to create synthetic container flows.

positional arguments:
  {create_input_spreadsheet,create_container_flow}
                        The action to perform
  filepath              The path to the XLSX file

options:
  -h, --help            show this help message and exit
  --overwrite           Whether existing files shall be overwritten
```

A short explanation of the commands:
- The command `create_input_spreadsheet` creates a spreadsheet file based on the current default distributions in 
  ConFlowGen.
- The command `create_container_flow` reads in a prepared spreadsheet file and creates synthetic container book data.
  The result is stored in an SQLite file right next to the spreadsheet file, using the same file name but a suitable 
  file extension.

## Example

The spreadsheet in this folder has been created by running the following command on the CLI:

```
$ conflowgen_spreadsheet_interface create_input_spreadsheet SpreadsheetInterface.xlsx
```

You can open it in your preferred spreadsheet application such as
MS Excel or LibreOffice Calc.

After having modified all the input data as desired, the following command on the CLI generated the container flow data:

```
$ conflowgen_spreadsheet_interface create_container_flow SpreadsheetInterface.xlsx
```

This results in the SQLite database `SpreadsheetInterface.sqlite`