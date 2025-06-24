import json
import pandas as pd
from jsonschema import validate, ValidationError
import copy

def load_schema(schema_path):
    with open(schema_path, 'r') as f:
        return json.load(f)


def preprocess_dataframe(df, schema):
    props = schema.get("properties", {})
    for field, rules in props.items():
        field_type = rules.get("type")
        if field_type == "array":
            # Convert pipe-separated values into arrays
            df[field] = df[field].fillna('').apply(lambda x: x.split('|') if isinstance(x, str) and x else [])

    return df

def validate_row(row, schema):
    errors = []
    parsed = {}
    props = schema.get("properties", {})
    required = schema.get("required", [])
    clean_schema = copy.deepcopy(schema)

    for field in required:
        if field not in row or row[field] is None or str(row[field]).strip() == "":
            errors.append(f"{field} is required")

    for field, rules in props.items():
        value = row.get(field)
        expected_type = rules.get("type")

        if value is None or (isinstance(value, float) and pd.isna(value)):
            continue

        try:
            if expected_type == "integer":
                int_val = int(float(value))
                if float(value) != int_val:
                    raise ValueError
                parsed[field] = int_val
            elif expected_type == "number":
                parsed[field] = float(value)
            elif expected_type == "boolean":
                val = str(value).lower()
                if val in ["true", "1"]:
                    parsed[field] = True
                elif val in ["false", "0"]:
                    parsed[field] = False
                else:
                    raise ValueError
            elif expected_type == "array":
                parsed[field] = value
            else:
                parsed[field] = value
        except Exception:
            clean_schema['properties'].pop(field, None)
            if(field in clean_schema['required']):
                clean_schema['required'].remove(field)
            errors.append(f"{field} has invalid {expected_type} value: {value}")

    try :
        validate(instance=parsed, schema=clean_schema)
    except ValidationError as e:
        errors.append(e.message)

    if errors:
            return False, errors

    return True, parsed


def validate_csv(csv_path, schema_path):
    print("Reading Template ...")
    schema = load_schema(schema_path)
    print("Template Loaded Successfully ✅")

    try:
        print("Reading CSV ...")
        df = pd.read_csv(csv_path)
        print("CSV file loaded successfully ✅")
    except Exception as e:
        print("❌ Failed to read CSV:", e)
        return

    df = preprocess_dataframe(df, schema)

    results = []
    parsed_rows = []

    for idx, row in df.iterrows():
        is_valid, outcome = validate_row(row, schema)
        if is_valid:
            parsed_rows.append(outcome)
        results.append({
            "row": idx + 2,
            "valid": is_valid,
            "errors": outcome if not is_valid else []
        })

    return results, parsed_rows