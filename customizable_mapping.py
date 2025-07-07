def map_row(row):
    images = [
                row['Image 1'] if isinstance(row['Image 1'], str) else '',
                row['Image 2'] if isinstance(row['Image 2'], str) else '',
                row['Image 3'] if isinstance(row['Image 3'], str) else '',
                row['Image 4'] if isinstance(row['Image 4'], str) else '',
                row['Image 5'] if isinstance(row['Image 5'], str) else '',
            ]
    
    non_null_images = []
    for i in images:
        if i != '':
            non_null_images.append(i)

    return [
        {},
        {
            "description": row['Description'],
            "overrideUrl": row['Override url'],
            "type": row['Type'].strip(),
            "nEWCUSTOMADDRESSWHAT3WORDS": row['NEW CUSTOM ADDRESS/WHAT3WORDS'],
            "latitude":row['Latitude'],
            "longitude": row['Longitude'],
            "region": row['Region'],
            "images": non_null_images,
            "descriptionwithHtml": row['Description (with html)'],
            "componentName" : row['Name']
        }
    ]
