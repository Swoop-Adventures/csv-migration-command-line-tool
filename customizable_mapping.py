from bs4 import BeautifulSoup
import pandas as pd


# ------------------------------
# Helper functions
# ------------------------------

from datetime import datetime

def normalize_date(date_str):
    if not isinstance(date_str, str) or not date_str.strip():
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

    
def extract_list_items(html_string):
    if not isinstance(html_string, str) or pd.isna(html_string):
        return []
    soup = BeautifulSoup(html_string, 'html.parser')
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

def parse_bed_configurations(value):
    options = {
        "single": "single",
        "double": "double",
        "twin": "twin",
        "triple": "triple",
        "quad": "quad",
        "bunk bed": "bunkBed",
        "bunkbed": "bunkBed",  # handle variations
        "cabin": "cabin"
    }
    result = {v: False for v in options.values()}

    if isinstance(value, str):
        for part in value.split(","):
            part_clean = part.strip().lower()
            for k, v in options.items():
                if k in part_clean:
                    result[v] = True
    return result


# ------------------------------
# Main hotel-level mapping
# ------------------------------
def safe_str(val):
    if pd.isna(val):
        return ""
    return str(val)

def map_row(row):
    # Handle images
    images = [row.get(f"Image {i}", '') for i in range(1, 6)]
    images = [img for img in images if isinstance(img, str) and img]
    num_inspections = 3
    inspections = []

    for i in range(num_inspections):
        inspected_by = row.get(f"inspection{i}_by", "")
        date_raw = row.get(f"inspection{i}_date", "")
        notes = row.get(f"inspection{i}_notes", "")

        date_str = normalize_date(date_raw)  # returns None if invalid

        inspections.append({
            "inspectedBy": inspected_by or "",
            "date": date_str if date_str else "",
            "inspectionNotes": notes or ""
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
                "foodDrinkDescription": row.get("Food & Drink Description") or None,
                "mealsAvailable": ([m.strip() for m in str(row.get("Meals Available", "")).split(",") if m.strip()]if isinstance(row.get("Meals Available"), str)else [])
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
                "checkInTime": row.get("Check in Time") or None,
                "checkOutTime": row.get("Check Out Time") or None,
                "breakfastStartTime": row.get("Breakfast Start Time") or None,
                "breakfastEndTime": row.get("Breakfast End Time") or None
            },
            "roomsCabinCategories": row.get('roomsCabinCategories'),
            "componentName" : row.get("Name")
        }
    ]

def safe_str_none(val):
    if pd.isna(val):
        return None
    return str(val)

def map_room_row(room):
    image = room.get("Image", "")
    return {
        "roomCabinName": room.get("Room/Cabin name") or None,
        "roomDescription": (
            room.get("Room/Cabin Description", "") or room.get("Room/Cabin description", "")
        ),
        "images": [image] if isinstance(image, str) and image else [],
        "size": str(room.get("Size") or ""),
        "bedConfigurations": parse_bed_configurations(room.get("Bed Configurations")) or None,
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
