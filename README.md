# CSV Migration Command Line Tool
This is a command line application that uses json schema to validate the imported csv file row by row using json validator.

## Before running application
- Ensure python is installed.
- run `pip install jsonschema pandas` to install required packages.

## To run application
- Enter command line `python app.py`.

## Important
- If the data is nested (or an array type), data need to be separated with "|" under one column. E.g. admin | editor.
