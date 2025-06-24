import os
from validate_csv_dynamic import validate_csv 
import json

def run_loop():
    print("🔁 CSV Validator App (Ctrl+C or type 'exit' to quit)")
    try:
        while True:
            csv_path = input("\nEnter CSV file path: ").strip()
            if csv_path.lower() == "exit":
                break
            schema_path = input("Enter JSON schema file path: ").strip()
            if schema_path.lower() == "exit":
                break

            if not os.path.exists(csv_path):
                print("❌ CSV file not found.")
                continue
            if not os.path.exists(schema_path):
                print("❌ Schema file not found.")
                continue

            try:
                results, parsed_json = validate_csv(csv_path, schema_path)
            except Exception as e:
                print(f"❌ Validation error: {e}")
                continue

            invalid = [r for r in results if not r["valid"]]
            if invalid:
                print("\n❌ Validation failed on the following rows:")
                for r in invalid:
                    print(f"Row {r['row']}:")
                    for err in r["errors"]:
                        print("  -", err)
            else:
                print("\n✅ All rows are valid!")
                insert = input("Do you want to insert into the database? (y/n): ").strip().lower()
                if insert == "y":
                    print("📦 Preview JSON:")
                    print(json.dumps(parsed_json[:3], indent=2))
                    
                    push = input("Are you sure to push these into database? (y/n): ").strip().lower()
                    if push == "y":
                        print("🛜 Calling API ...")
                        # Calling api and update into database.
                        print("✅ Data inserted into database.")
                else:
                    print("⏩ Skipping database insert.")

    except KeyboardInterrupt:
        print("\n👋 Exiting the app. Goodbye!")
        

if __name__ == "__main__":
    run_loop()