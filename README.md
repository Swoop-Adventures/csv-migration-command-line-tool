# CSV Migration Command Line Tool

This is a command line application that uses json schema to validate the imported csv file row by row using json validator.

## Before running application

- Ensure python is installed.
- run `pip install jsonschema pandas requests python-dotenv` to install required packages.
- csv file ends with .csv should be ready to input.

## To run application

- Enter command line `python app.py`.

## Guide to use

You will need:

- To customize `map_row` based on how you want the data to be extracted from each csv row.
- The `map_row` function must map the data from top to lowest level template structure.
- To have an array of template ids from top to low level and replace the value of variable `template_ids` in file line 8 `app.py`.

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

`template_ids` variable should be like this.

```python
template_ids=["template_base_v1_id", "template_middle_east_adventure_v2_id", "template_hotel_v4_id"]
```
