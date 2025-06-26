# CSV Migration Command Line Tool

This is a command-line application that uses JSON schema to validate the imported CSV file row by row using JSON validator.

## Before running the application

- Ensure Python is installed.
- Run `pip install jsonschema pandas requests python-dotenv` to install required packages.
- CSV file ends with .csv should be ready to input.
- Configure .env file

## To run the application

- Enter the command line `python app.py`.

## Guide to use

You will need:

- To customize `map_row` based on how you want the data to be extracted from each CSV row.
- The `map_row` function must map the data from the top to the lowest level template structure.
- For by step user guide, [Visit This Google Doc](https://docs.google.com/document/d/1RmSBVvFJEpZxZq6Lquh9uBI92rMPAu33P52AtbdGPGk/edit?usp=sharing)

## Example

Let's say we have a template hierarchy:

```
Base
├── Middle East Adventure
│ ├── Hotel
```

`map_row` should be like:

```python
def map_row(row):
    return [
        {}, # <--- Base
        { # <--- Middle East Adventure
            "numberOfPeople" : row['Total Number of People'],
            "countryName" : row['Country Name']
        },
        { # <--- Hotel
            "hotelName" : row['Hotel Name']
        }
    ]
```
