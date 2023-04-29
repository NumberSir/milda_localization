from pathlib import Path

VERSION = "0.2.7.1"

"""游戏 data 文件夹绝对路径"""
DIR_ROOT = Path("D:\Joy\Butter\Daily Lives of My Countryside v0.2.7.1 (PC) (Bugfix)\www\data").absolute()
DIR_PROJECT = Path(__file__).parent
DIR_BACKUP = DIR_PROJECT / "BACKUP"

DIR_RESULTS = DIR_PROJECT / "data" / "results"
DIR_SUPPORT = DIR_PROJECT / "data" / "support"
DIR_FETCHES = DIR_PROJECT / "data" / "fetches"
DIR_PROCESS = DIR_PROJECT / "data" / "processes"
DIR_MACHINE = DIR_PROJECT / "data" / "machine"
DIR_PARATRANZ = DIR_PROJECT / "data" / "paratranz"
DIR_LOCALIZATIONS = DIR_PROJECT / "data" / "localizations"
DIR_LOCALIZATIONS_FILES = DIR_LOCALIZATIONS / "files" / VERSION

RAW_FILES = {
    "items": "Items.json",
    "system": "System.json",
    "common": "CommonEvents.json",
    "maps": "Map{:0>3d}.json"
}

MAPS_COUNT = 70
CODES_NEEDED_TRANSLATION = {
    "对话": 401,
    "选项": 102
}

__all__ = [
    "VERSION",

    "DIR_ROOT",
    "DIR_PROJECT",
    "DIR_BACKUP",
    "DIR_RESULTS",
    "DIR_SUPPORT",
    "DIR_FETCHES",
    "DIR_PROCESS",
    "DIR_MACHINE",
    "DIR_PARATRANZ",
    "DIR_LOCALIZATIONS",
    "DIR_LOCALIZATIONS_FILES",

    "RAW_FILES",
    "MAPS_COUNT",
    "CODES_NEEDED_TRANSLATION"
]