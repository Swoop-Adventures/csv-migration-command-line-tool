import unittest
import tempfile
import os
import json
import pandas as pd
from validate_csv_dynamic import validate_csv  # Replace with actual module

class TestCSVValidator(unittest.TestCase):

    def setUp(self):
        self.schema = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "is_active": {"type": "boolean"},
                "created_at": {"type": "string", "format": "date"}
            },
            "required": ["id", "name", "is_active"]
        }

        self.temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        self.temp_csv.close()

        self.temp_schema = tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".json")
        json.dump(self.schema, self.temp_schema)
        self.temp_schema.close()

    def tearDown(self):
        os.unlink(self.temp_csv.name)
        os.unlink(self.temp_schema.name)

    def test_valid_csv_should_pass(self):
        df = pd.DataFrame([
            {"id": 1, "name": "Alice", "is_active": 1, "created_at": "2024-01-01"},
            {"id": 2, "name": "Bob", "is_active": 0, "created_at": "2024-02-01"}
        ])
        df.to_csv(self.temp_csv.name, index=False)
        results, parsed = validate_csv(self.temp_csv.name, self.temp_schema.name)
        self.assertTrue(all(r["valid"] for r in results))
        self.assertEqual(len(parsed), 2)

    def test_invalid_boolean_should_fail(self):
        df = pd.DataFrame([
            {"id": 3, "name": "Charlie", "is_active": "maybe", "created_at": "2024-03-01"}
        ])
        df.to_csv(self.temp_csv.name, index=False)
        results, parsed = validate_csv(self.temp_csv.name, self.temp_schema.name)
        self.assertFalse(results[0]["valid"])
        self.assertIn("is_active", " ".join(results[0]["errors"]))
        self.assertEqual(len(parsed), 0)

    def test_missing_required_field_should_fail(self):
        df = pd.DataFrame([
            {"id": 4, "is_active": 1, "created_at": "2024-04-01"}  # missing "name"
        ])
        df.to_csv(self.temp_csv.name, index=False)
        results, parsed = validate_csv(self.temp_csv.name, self.temp_schema.name)
        self.assertFalse(results[0]["valid"])
        self.assertIn("name is required", " ".join(results[0]["errors"]))
        self.assertEqual(len(parsed), 0)

    def test_invalid_date_format_should_fail(self):
        df = pd.DataFrame([
            {"id": 5, "name": "Daisy", "is_active": 1, "created_at": "31-12-2023"}
        ])
        df.to_csv(self.temp_csv.name, index=False)
        results, parsed = validate_csv(self.temp_csv.name, self.temp_schema.name)
        self.assertFalse(results[0]["valid"])
        self.assertIn("created_at", " ".join(results[0]["errors"]))
        self.assertEqual(len(parsed), 0)
