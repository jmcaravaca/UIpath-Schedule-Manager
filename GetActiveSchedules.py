import requests
import json
import urllib.parse

#---09/02/2023: Este script es un arreglo rápido para el mantenimiento de este fin de semana. NO usar de forma permanente
base_url = "https://orchestratorsta.masmovil.com"
#---Endpoints---

endpoint_Auth = "/api/Account/Authenticate"
endpoint_GetFolders = "/odata/Folders"
endpoint_GetTriggers = "/odata/ProcessSchedules"
endpoint_EnableTriggers = "/odata/ProcessSchedules/UiPath.Server.Configuration.OData.SetEnabled"


#---Credentials

user = "****"
passw =  "****"

#-------GET TOKEN-------------
url = urllib.parse.urljoin(base_url, endpoint_Auth)

payload = {
    "tenancyName": "Default",
    "usernameOrEmailAddress": user,
    "password": passw
}

headers = {"Content-Type": "application/json"}
response = requests.request("POST", url, json=payload, headers=headers)
token = response.json()["result"]

#------GET Folders (Organization Units)
dfolders = {} # Dict of foldername - id

url = urllib.parse.urljoin(base_url, endpoint_GetFolders)
querystring = {"$select":"FullyQualifiedName,Id","$count":"false"}
payload = ""
headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        }
payload = ""

response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
resjson = response.json()["value"]

for res in resjson:
    dfolders[res["FullyQualifiedName"]] = int(res["Id"])


dtriggers = {} #Key is Folder Name, values is list of dicts of (schedule name, schedule_id)

for folder_name, folder_id in dfolders.items():
    try:
        url = urllib.parse.urljoin(base_url, endpoint_GetTriggers)
        querystring = {"$filter":"Enabled eq true","$select":"Name,Id"}
        payload = ""
        headers = {
            "X-UIPATH-OrganizationUnitId": str(folder_id) ,
            "Authorization" : "Bearer " + token    
        }
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        print(response.text)
        if response.json()["@odata.count"] > 0:
            dtriggers[folder_name] = []
        resjson = response.json()["value"]
        for res in resjson:
            dtriggers[folder_name].append({res["Name"]: res["Id"]})
    except Exception as e:
        print(Exception)

# DTRiggers, DFolders get

# Serializing json
json_object = json.dumps(dtriggers, indent=4)
 
# Writing to EnabledTriggers.json
with open("EnabledTriggers.json", "w") as outfile:
    outfile.write(json_object)

url = urllib.parse.urljoin(base_url, endpoint_EnableTriggers)

for folder_name, listofitems in dtriggers.items():
    try:
        pass

        folder_id = dfolders[folder_name]
        print("Folder Id: " + str(folder_id))
        payload = {
            "enabled": True,
            "scheduleIds": [value for x in listofitems for value in x.values()]
        }

        headers = {
            "Content-Type": "application/json",
            "X-UIPATH-OrganizationUnitId": str(folder_id),
            "Authorization": "Bearer " + token
        }
        response = requests.request("POST", url, json=payload, headers=headers)
        print(response.text)
    except Exception as e:
        print(e)


