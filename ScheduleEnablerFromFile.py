import ScheduleManager
from credsecrets import *
from loguru import logger
from pathlib import Path

logger.info("Starting execution...")


CONFIG_FILE = "settings.json"
TRIGGERS_PATH = "SavedSchedules"
ScheduleManager = ScheduleManager.UIPathScheduleManager(CONFIG_FILE, CREDUSER, CREDPASS, CREDTYPE, OAuthAppType, OAuthGrantType)

folders = ScheduleManager.GetFolders()
logger.info("Obtained folders")

#Get all JSON Saved Schedules
triggers_path = Path(TRIGGERS_PATH)
file_list = list(triggers_path.glob("**/*.json"))

for file in file_list:
    logger.info("Checking file: {0}", str(file))
    triggers = ScheduleManager.LoadTriggers(str(file))
    for foldername, values in triggers.items():
        ScheduleManager.ToggleSchedules(True, ScheduleManager._FlattenScheduleIDs(triggers, foldername), folders[foldername])
    logger.info("Enabled Schedules")

logger.info("Ending execution...")
