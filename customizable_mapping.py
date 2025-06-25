def map_row(row):
    return [
        {},
        {
            "numberOfPeople" : row['Total Number of People'],
            "countryName" : row['Country Name']
        },
        {
            "hotelName" : row['Hotel Name']
        }
    ]
