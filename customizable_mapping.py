from bs4 import BeautifulSoup
import pandas as pd


# ------------------------------
# Helper functions
# ------------------------------
def extract_list_items(html_string):
    soup = BeautifulSoup(html_string or '', 'html.parser')
    return [li.get_text(strip=True) for li in soup.find_all('li')]
def normalize_facility(value):
    if isinstance(value, str):
        val = value.lower()
        if val in ['true', 'yes', 'included']:
            return 'Included'
        elif val in ['extra cost', 'paid', 'additional']:
            return 'Extra Cost'
        elif val in ['false', 'no', 'not included']:
            return 'No'
    return "No"
def normalize_boolean(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        val = value.lower()
        return val in ['yes', 'true', 'included']
    return False
def normalize_enum(value, valid_options):
    if isinstance(value, str):
        val = value.capitalize()
        return val if val in valid_options else "No"
    return "No"

# ------------------------------
# Main hotel-level mapping
# ------------------------------
def map_row(row):
    # Handle images
    images = [row.get(f"Image {i}", '') for i in range(1, 6)]
    images = [img for img in images if isinstance(img, str) and img]

    # Handle inspections
    inspections = []
    for i in range(1, 4):
        inspected_by = row.get(f"Inspected by {i}", "")
        date = row.get(f"Date {i}", "")
        notes = row.get(f"Inspection Notes {i}", "")
        if inspected_by or date or notes:
            inspections.append({
                "inspectedBy": inspected_by,
                "date": date,
                "inspectionNotes": "" if pd.isna(notes) else notes
            })
        
    return [
        {},
        {
            "description": {
                 "website": None,
                "quote": None,
                "finalItinerary": None
            },
            "region": row.get("Region"),
            "type": row.get("Type"),
            "images": images,
            "facilities": {
                "library": normalize_boolean(row.get("Library")),
                "shop": normalize_boolean(row.get("Shop")),
                "restaurant": normalize_boolean(row.get("Restaurant")),
                "additionalRestaurants": normalize_boolean(row.get("Additional Restaurants")),
                "bar": normalize_boolean(row.get("Bar")),
                "gym": normalize_facility(row.get("Gym")),
                "spa": normalize_facility(row.get("Spa")),
                "jacuzzi": normalize_facility(row.get("Jacuzzi")),
                "pool": normalize_facility(row.get("Pool")),
                "sauna": normalize_facility(row.get("Sauna")),
                "steamRoom": normalize_facility(row.get("Steam Room")),
                "massage": normalize_facility(row.get("Massage")),
                "elevator": normalize_boolean(row.get("Elevator")),
                "laundry": normalize_facility(row.get("Laundry")),
                "roomService": normalize_boolean(row.get("Room Service"))
            },
            "foodDrink": {
                "foodDrinkDescription": row.get("Food & Drink Description", ""),
                "mealsAvailable": [m for m in row.get("Meals Available", "").split(",") if m]
            },
            "connectivity": {
                "wiFi": row.get("WiFi"),
                "phoneSignal": row.get("Phone Signal")
            },
            "facts": {
                "capacity": row.get("Capacity"),
                "yearBuilt": row.get("Year Built")
            },
            "inspections": inspections,
            "swoopSays": {
                "swooper": row.get("Swooper"),
                "whatTheySayAboutThisAccommodation": row.get("What they say about this accommodation"),
                "whatWeLikeAboutThisHotel": extract_list_items(row.get("What we like about this hotel", "")),
                "weThinkItsWorthNoting": extract_list_items(row.get("We think its worth noting", "")),
                "recommendations": row.get("Recommendations")
            },
            "video": row.get("Video") if isinstance(row.get("Video"), str) and row.get("Video").startswith("http") else None,
            "partners": row.get("Partners"),
            "minimumAge": row.get("Minimum Age"),
            "timings": {
                "checkInTime": row.get("Check in Time") or "",
                "checkOutTime": row.get("Check Out Time") or "",
                "breakfastStartTime": row.get("Breakfast Start Time") or "",
                "breakfastEndTime": row.get("Breakfast End Time") or ""
            },
            "roomsCabinCategories": row.get('roomsCabinCategories'),
            "componentName" : row.get("Name")
        }
    ]

def map_room_row(room):
    image = room.get("Image", "")
    return {
        "roomCabinName": room.get("Room/Cabin name", ""),
        "roomDescription": (
            room.get("Room/Cabin Description", "") or room.get("Room/Cabin description", "")
        ),
        "images": [image] if isinstance(image, str) and image else [],
        "size": room.get("Size", ""),
        "bedConfigurations": room.get("Bed Configurations", ""),
        "bathroomType": "Private" if "private" in str(room.get("Bathroom Type", "")).lower() else "Shared",
        "bath": normalize_boolean(room.get("Bath")),
        "balcony": normalize_boolean(room.get("Balcony")),
        "logBurnerFireplace": normalize_boolean(room.get("Log Burner/Fireplace")),
        "abilityToAddAnExtraBed": normalize_boolean(room.get("Ability to add an extra bed")),
        "teaCoffeeMakingFacilities": normalize_boolean(room.get("Tea/Coffee Making Facilities")),
        "fridgeMiniBar": normalize_boolean(room.get("Fridge/Mini Bar")),
        "privateJacuzziHotTub": normalize_boolean(room.get("Private Jacuzzi/Hot Tub")),
        "wiFiInRoom": normalize_boolean(room.get("WiFi in Room")),
        "tV": normalize_boolean(room.get("TV")),
        "soundSystem": normalize_boolean(room.get("Sound System")),
        "privateLoungeArea": normalize_enum(room.get("Private Lounge Area"), ["Integrated", "Separate", "No"]),
        "privateDiningArea": normalize_enum(room.get("Private Dining Area"), ["Integrated", "Private", "No"]),
        "hairdryer": normalize_boolean(room.get("Hairdryer")),
        "aircon": normalize_boolean(room.get("Aircon")),
        "renewableEnergy": normalize_boolean(room.get("Do they use renewable energy?")),
        'accomoName' : room.get("Hotel/Vessel")
    }