import os
from validate_csv_dynamic import validate_csv 
from core_data_services import CoreDataService

def run_loop():
    
    # Template ids from top to bottom level
    template_ids = ["template_aca16a46ec3842ca85d182ee9348f627", "template_c96dc7605db04f3eb94f5d57cd1756dc", "template_745b961ba1e04985a49f0dd58efae85a"]
    core_data_service = CoreDataService(template_ids)
    json_schemas = core_data_service.getSchemaWithArrayLevel()

    print("🔁 CSV Validator App (Ctrl+C or type 'exit' to quit)")
    try:
        while True:
            csv_path = input("\nEnter CSV file path: ").strip()
            if csv_path.lower() == "exit":
                break
            # schema_path = input("Enter JSON schema file path: ").strip()
            # if schema_path.lower() == "exit":
            #     break

            if not os.path.exists(csv_path):
                print("❌ CSV file not found.")
                continue
            # if not os.path.exists(schema_path):
            #     print("❌ Schema file not found.")
            #     continue

            try:
                results, parsed_json = validate_csv(csv_path, json_schemas)
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
                print("Please correct the above before retry")
            else:
                print("\n✅ All rows are valid!")
                insert = input("Do you want to insert into the database? (y/n): ").strip().lower()
                if insert == "y":
                    print("📦 Preview JSON:")
                    print(parsed_json)
                    
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