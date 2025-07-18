import json
import pandas as pd
from jsonschema import validate, ValidationError
from customizable_mapping import map_row, map_room_row
import copy

_SCALAR_TYPES = {"integer", "number", "boolean", "string"}

def load_schema(schema_path):
    with open(schema_path, 'r') as f:
        return json.load(f)

def _coerce_scalar(value, expected_type):
    """
    Try to coerce `value` into `expected_type`.
    Raise ValueError on failure.
    """
    if expected_type == "integer":
        i = int(float(value))
        if float(value) != i:
            raise ValueError
        return i
    if expected_type == "number":
        return float(value)
    if expected_type == "boolean":
        val = str(value).lower()
        if val in ("true", "1"):
            return True
        if val in ("false", "0"):
            return False
        raise ValueError
    # string – just cast
    return str(value)

def _parse_node(node, schema, path=""):
    """
    Recursively parse a piece of data (`node`) according to `schema`.

    Returns:
        parsed_node   – only fields that parsed OK
        pruned_schema – schema minus the paths that failed
        errors        – list of (path, message) tuples
    """
    errors = []
    pruned_schema = copy.deepcopy(schema)

    if schema.get("type") == "object":
        parsed = {}
        pruned_props = {}
        props = schema.get("properties", {})
        required = schema.get("required", [])

        # ensure we have a dict
        if not isinstance(node, dict):
            errors.append((path, f"expected object, got {type(node).__name__}"))
            return None, {}, errors

        # required checks (missing keys)
        for key in required:
            if key not in node or node[key] in (None, "", float("nan")):
                errors.append((f"{path}.{key}" if path else key, "is required"))

        # iterate all declared properties
        for key, subschema in props.items():
            subpath = f"{path}.{key}" if path else key
            value = node.get(key, None)

            # ignore truly missing & optional
            if value is None or (isinstance(value, float) and pd.isna(value)):
                continue
            parsed_sub, pruned_subschema, sub_errors = _parse_node(value, subschema, subpath)

            if sub_errors:
                errors.extend(sub_errors)
            else:
                parsed[key] = parsed_sub 
                pruned_props[key] = pruned_subschema

        # rebuild pruned_schema for this object level so that it can be used in next recursive
        pruned_schema["properties"] = pruned_props
        pruned_schema["required"] = [r for r in required if r in pruned_props]

        return parsed, pruned_schema, errors

    expected_type = schema.get("type")
    try:
        if expected_type in _SCALAR_TYPES:
            parsed_scalar = _coerce_scalar(node, expected_type)
            return parsed_scalar, pruned_schema, errors
        else:
            return node, pruned_schema, errors
    except Exception as exc:
        errors.append((path, f"invalid {expected_type}: {node} ({exc})"))
        return None, {}, errors

def validate_row(row: dict, schema: dict, row_number: int = None):
    """
    Parse & validate one row (dict) against a nested JSON Schema.
    Returns (is_valid: bool, parsed_or_errors)
    """
    parsed, pruned_schema, parse_errors = _parse_node(row, schema)

    if parse_errors:
        # convert tuple list to simple strings for caller
        return False, [f"Row {row_number}: {p}: {m}" for p, m in parse_errors]

    try:
        validate(instance=parsed, schema=pruned_schema)
        return True, parsed
    except ValidationError as e:
        # build similar path.message style
        path = ".".join([str(p) for p in e.path]) or "root"
        return False, [f"Row {row_number}: {path}: {e.message}"]

def validate_csv(room_csv_path, csv_path, schemas):
    try:

        # Load room csv and accommodation csv separately
        print("Reading Room CSV ...")
        df_room = pd.read_csv(room_csv_path)
        print("Room CSV file loaded successfully ✅")

        print("Reading Accommodation CSV ...")
        df = pd.read_csv(csv_path)
        print("Accommodation CSV file loaded successfully ✅")

        # Ensure the column exists first
        df['roomsCabinCategories'] = None

        mapped_room_data = df_room.apply(map_room_row, axis=1).tolist()

        # Map room facilites array into accommodation data frame
        for idx, row in df.iterrows():
            name = row['Name']
            matching_facilities = [
                {k: v for k, v in item.items() if k != 'accomoName'}
                for item in mapped_room_data
                if item['accomoName'] == name
            ]
            # Convert to list of dicts (or just a list of values if you prefer)
            df.at[idx, 'roomsCabinCategories'] = matching_facilities

    except Exception as e:
        print("❌ Failed to read CSV:", e)
        return

    mapped_data = df.apply(map_row, axis=1).tolist()

    results = []
    parsed_rows = []

    for idx, row in enumerate(mapped_data, start=2):
        final_res = []
        for level, data in enumerate(row):
            schema = schemas[level]
            is_valid, outcome = validate_row(data, schema, row_number=idx)
            results.append({
                "row": idx + 2,
                "valid": is_valid,
                "errors": outcome if not is_valid else []
            })
            if is_valid:
                if 'componentName' in data and data['componentName'] != None:
                    outcome['componentName'] = data['componentName']
                final_res.append(outcome)
            else:
                final_res.append({})
        parsed_rows.append(final_res)
    return results, parsed_rows