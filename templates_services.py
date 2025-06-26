from core_data_services import CoreDataService
from utils import printTemplateList

def getTemplateIds():
    template_ids = []
    while True:
        template_name = input("Enter template name: ").strip()
        template_list = CoreDataService.getTemplatesList({'name' : template_name ,'limit' : 5000})
        if(len(template_list) == 0):
            print("❌ No template found, try to enter correct template name")
            continue
        printTemplateList(template_list)
        while True:
            template_idx = input("\nPlease enter the No. of preferred schema to proceed (e.g. 1): ").strip()
            if int(template_idx) > len(template_list) or int(template_idx) < 0:
                print("ℹ️ Please enter valid No.")
                continue
            else:
                break
        selected_template = template_list[int(template_idx) - 1]
        template_ids.append(selected_template['id'])
        if selected_template['parentRevisionGroupId']:
            template_ids = getTemplateLists(selected_template, template_ids)
            break
    template_ids.reverse()
    return template_ids

def getTemplateLists(selected_template, template_ids = []):
    print("Parent Template Found.")
    print("Fetching parent template list ...")
    template_list = CoreDataService.getTemplatesList({'revisionGroupId' : selected_template['parentRevisionGroupId'] ,'limit' : 5000})
    printTemplateList(template_list)
    while True:
        template_idx = input("\nPlease enter the No. of preferred schema to proceed (e.g. 1): ").strip()
        if int(template_idx) > len(template_list) or int(template_idx) < 0:
            print("ℹ️ Please enter valid No.")
            continue
        else:
            break
    selected_template = template_list[int(template_idx) - 1]
    template_ids.append(selected_template['id'])
    if selected_template['parentRevisionGroupId']:
        return getTemplateLists(selected_template, template_ids)
    else:
        return template_ids
    
