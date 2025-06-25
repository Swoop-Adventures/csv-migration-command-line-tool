import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

class CoreDataService:
    def __init__(self, template_ids):
        self.template_ids = template_ids # From top to bottom template ids array E.g. [lvl-1, lvl-2, lvl-3, lvl-4]
        self.service_url = os.environ['SERVICE_URL']

    def getTemplatesList(self, params):
        res = requests.get(self.service_url + "/core-data-service/v1/templates", params=params)
        response = res.json()
        return response

    def getSchemaWithArrayLevel(self):
        templates = [] # From top to bottom template
        for idx, template_id in enumerate(self.template_ids):
            res = requests.get(self.service_url + "/core-data-service/v1/templates/" + template_id)
            response = res.json()
            if(response["jsonSchema"]):
                json_schema = json.loads(response['jsonSchema'])
                templates.append(json_schema)
                if(idx == len(self.template_ids) - 1):
                    self.template_name = response['name']
                    self.template_id = response['id']
            else:
                templates.append({})
        return templates

    def pushValidRowToDB(self, parsed_data):
        for idx, data in enumerate(parsed_data):
            fields = []
            for i in range(len(self.template_ids) - 1, -1, -1):
                d = data[i]
                t_id = self.template_ids[i]
                fields.append({
                    "templateID" : t_id,
                    "data" : d
                })
            payload= {
                "templateId" : self.template_id,
                "name" : self.template_name,
                "fields" : fields,
                "children" : []
            }
            res = requests.post(self.service_url + "/core-data-service/v1/components", json=payload)
            if res.status_code == 201:
                print(f"✅ Row {idx + 1} has been pushed!")
            else:
                print(f"❌ Failed to push Row {idx + 1}")
 
