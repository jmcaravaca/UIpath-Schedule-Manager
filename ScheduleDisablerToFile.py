import ScheduleManager
import os
from credsecrets import *
from loguru import logger

logger.info("Starting execution...")

CONFIG_FILE = "settings.json"

ScheduleManager = ScheduleManager.UIPathScheduleManager(CONFIG_FILE, CREDUSER, CREDPASS, CREDTYPE, OAuthAppType, OAuthGrantType)

folders = ScheduleManager.GetFolders()
logger.info("Obtained folders")
for foldername, folderid in folders.items():
    logger.info("Checking folder: {0}", foldername)
    triggers = ScheduleManager.GetTriggers(folderid, foldername, True) 
    if triggers: # Proceed only if we found triggers
        logger.info("Triggers found: {0}", len(triggers))
        savefolder =  os.path.join("SavedSchedules", os.path.normpath(foldername)) 
        #Orchestratorfolders are always separated by / so subfolders will be created accordingly in Windows
        if not os.path.exists(savefolder):
            os.makedirs(savefolder, exist_ok=True)
            logger.info("Created folder to save triggers: {0}", savefolder)
        savepath = os.path.join(savefolder, "Schedules.json")
        ScheduleManager.SaveTriggers(savepath, triggers)
        logger.info("Saved triggers at {0}", savefolder)
        ScheduleManager.ToggleSchedules(False, ScheduleManager._FlattenScheduleIDs(triggers, foldername), folderid)
        logger.info("Enabled Schedules")

    

logger.info("Ending execution...")