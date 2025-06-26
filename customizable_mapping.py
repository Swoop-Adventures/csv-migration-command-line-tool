def map_row(row):
    return [
        {},
        {
            "numberOfPeople" : row['Total Number of People'],
            "countryName" : row['Country Name']
        },
        {
            "hotelName" : row['Hotel Name'],
            "componentName" : row['Hotel Name'] # can be whatever value from the row. It will be displayed as component name
        }
    ]
