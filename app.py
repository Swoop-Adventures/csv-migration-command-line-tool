import os
from validate_csv_dynamic import validate_csv 
from core_data_services import CoreDataService
from templates_services import getTemplateIds
import json

def run_loop():
    
    # Template ids from top to bottom level
    print("🔁 CSV Validator and Migration App (Ctrl+C or type 'exit' to quit)")

    try:
        template_ids = []

        if len(template_ids) == 0:
            template_ids = getTemplateIds()

        core_data_service = CoreDataService(template_ids)
        json_schemas = core_data_service.getSchemaWithArrayLevel()

        print("Fetched JSON Schema: ")
        print(json.dumps(json_schemas, indent= 2))
        print('--------------------------------------------------------------------')
        print(f"Friendly Reminder: copy and paste this array {template_ids} into template_ids variable if it is required in future.")
        
        while True:
            csv_path = input("\nEnter CSV file path: ").strip()
            if csv_path.lower() == "exit":
                break

            if not os.path.exists(csv_path):
                print("❌ CSV file not found.")
                continue

            try:
                results, parsed_json = validate_csv(csv_path, json_schemas)
            except Exception as e:
                print(f"❌ Validation error: {e}")
                continue

            invalid = [r for r in results if not r["valid"]]
            if invalid:
                print("\n❌ Validation failed on the following rows:")
                for r in invalid:
                    for err in r["errors"]:
                        print("  -", err)
                print("Please correct the above before retry")
            else:
                print("\n✅ All rows are valid!")
                insert = input("Do you want to insert into the database? (y/n): ").strip().lower()
                if insert == "y":
                    print("📦 Preview JSON:")
                    print(json.dumps(parsed_json, indent = 2))
                    
                    push = input("Are you sure to push these into database? (y/n): ").strip().lower()
                    if push == "y":
                        print("🛜 Calling API ...")
                        core_data_service.pushValidRowToDB(parsed_json)
                        print("✅ Data inserted into database.")
                else:
                    print("⏩ Skipping database insert.")

    except KeyboardInterrupt:
        print("\n👋 Exiting the app. Goodbye!")
        

if __name__ == "__main__":
    run_loop()