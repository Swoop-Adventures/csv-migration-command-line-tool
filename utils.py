import json

def printTemplateList(template_list):
    for idx, t in enumerate(template_list):
        json_schema = json.loads(t['jsonSchema'])
        print(f"{idx + 1} .")
        print(f"version : {t['version']}")
        print(json.dumps(json_schema, indent= 2))
        print ("__________________________________________")