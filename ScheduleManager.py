import requests
import json
import urllib.parse
from loguru import logger

#TODO Error handling

class UIPathScheduleManager():
    """Main Class for Schedule Manager.
    INPUTS:
    - url: Base url of the orchestrator
    - configfile: Path with the settings.json file
    - creduser: The username (or client id) to auth
    - credpass: The password (or client secret) to auth
    - credtype: The type of credential: (UserPass, OAuth2)
    - OAuthAppType: The type of OAuth2: (Confidential, Non-Confidential)
    - OAuthGrantType: The type of grant (User, Application)
    """
    def __init__(self, configfile:str, creduser:str, credpass:str, credtype:str, OAuthAppType:str, OAuthGrantType:str):
        with open(configfile) as json_file: #TODO check that it is a json file
            self.cfg = json.load(json_file)
        self.token = ""
        #TODO: get token and check type of credential
        #TODO OAUTH2
        self.credtype = credtype
        self.creduser = creduser
        self.credpass = credpass
        self.OAuthAppType = OAuthAppType
        self.OAuthGrantType = OAuthGrantType
        self.dfolders = {} # dict[foldername] = id
        self.dtriggers = {} # dict[foldername] = {schedulename:id, (...)}
        self.AuthUserPass()
    
    def AuthUserPass(self):
        """Get Auth Token Using User and Pass. Updates token in class and returns it"""
        #TODO RefreshToken?
        url = urllib.parse.urljoin(self.cfg["baseurl"], self.cfg["endpoint_Auth"])
        payload = {
            "tenancyName": self.cfg["tenantName"],
            "usernameOrEmailAddress": self.creduser,
            "password": self.credpass
        }

        headers = {"Content-Type": "application/json"}
        response = requests.request("POST", url, json=payload, headers=headers)
        try:
            self.token = response.json()["result"]
            logger.debug("Obtained auth token")
            return self.token
        except Exception as e:
            logger.error("Error when getting auth token")
            logger.error(e)
            raise e
    
    def GetFolders(self):
        #------GET Folders (Organization Units)
        self.dfolders = {} # Dict of foldername - id
        url = urllib.parse.urljoin(self.cfg["baseurl"], self.cfg["endpoint_GetFolders"])
        querystring = {"$select":"FullyQualifiedName,Id","$count":"false"}
        payload = ""
        headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + self.token
                }
        payload = ""
        
        response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
        try:
            resjson = response.json()["value"]
            logger.debug("Getting folders dict")
            for res in resjson:
                self.dfolders[res["FullyQualifiedName"]] = int(res["Id"])
            return self.dfolders
        except Exception as e:
            logger.error("Error when getting folders:")
            logger.error(e)
    
    def GetTriggers(self, OrgUnitID:int, OrgUnitName:str, enabled:bool):        
        """Get All Triggers From OrgUnit 
        enabled: if True it will only get triggers that are 'enabled' otherwise it will get all triggers"""
        dtriggers = {}
        url = urllib.parse.urljoin(self.cfg["baseurl"], self.cfg["endpoint_GetTriggers"])
        try:
            querystring = {"$filter":"Enabled eq true","$select":"Name,Id"}
            payload = ""
            headers = {
                "X-UIPATH-OrganizationUnitId": str(OrgUnitID) ,
                "Authorization" : "Bearer " + self.token
            }
            response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
            if response.json()["@odata.count"] > 0:
                dtriggers[OrgUnitName] = {}
            resjson = response.json()["value"]
            logger.debug("Adding triggers to dict")
            for res in resjson:
                dtriggers[OrgUnitName][res["Name"]] = res["Id"]
        except Exception as e:
            logger.error("Error when getting schedules:")
            logger.error(e)
        return dtriggers
            
    def _FlattenScheduleIDs(self, dtriggers:dict, foldername:str):
        """ Flatens a dictionary to a scheduleid list
            dtriggers[foldername] = {schedulename:id, (...)}"""
        return [value for value in dtriggers[foldername].values()] # Flatten schedule ids from dtrigger    
       
    def ToggleSchedules(self, enabled:bool, scheduleids:list, OrgUnitID:int):
        """Toggle Schedule IDs in specified folder"""
        url = urllib.parse.urljoin(self.cfg["baseurl"], self.cfg["endpoint_ToggleSchedules"])
        try:
            pass           
            payload = {
                "enabled": enabled,
                "scheduleIds": scheduleids # Flatten schedule ids
            }
            headers = {
                "Content-Type": "application/json",
                "X-UIPATH-OrganizationUnitId": str(OrgUnitID),
                "Authorization": "Bearer " + self.token
            }
            response = requests.request("POST", url, json=payload, headers=headers)
            logger.debug("Schedules toggled {0}", enabled)
        except Exception as e:
            logger.error("Error when toggling schedules:")
            logger.error(e)

    def SaveTriggers(self, filepath:str, dtriggers:dict):
        """Save triggers to a Json"""
        json_object = json.dumps(dtriggers, indent=4)
        # Writing to filepath json
        with open(filepath, "w") as outfile:
            outfile.write(json_object)
    
    def LoadTriggers(self, filepath:str):
        with open(filepath) as json_file: #TODO check that it is a json file
            dtriggers = json.load(json_file)
            return dtriggers
        




    