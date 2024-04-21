import json
import os
import shutil
import re
import subprocess
import zipfile

import httpx

from consts import *
from models import *
from log import *
from utils import *


class Translation:
    def __init__(self):
        ...

    @classmethod
    def init_dirs(cls):
        if not DIR_BACKUP.exists():
            os.makedirs(DIR_BACKUP)
        for file in os.listdir(DIR_BACKUP):
            if file == RAW_FILES["quests"]:
                shutil.copyfile(DIR_BACKUP / file, FILE_QUESTS)
                continue
            shutil.copyfile(DIR_BACKUP / file, DIR_ROOT / file)

        os.makedirs(DIR_FETCHES, exist_ok=True)
        os.makedirs(DIR_SUPPORT, exist_ok=True)
        os.makedirs(DIR_PROCESS, exist_ok=True)
        os.makedirs(DIR_PARATRANZ, exist_ok=True)
        os.makedirs(DIR_DOWNLOAD, exist_ok=True)
        os.makedirs(DIR_LOCALIZATIONS_FILES, exist_ok=True)
        shutil.copytree(DIR_BACKUP, DIR_RESULTS)

    """ FETCH """
    @classmethod
    def fetch_all(cls):
        logger.info("##### STARTING FETCHING ALL FILES...")
        cls.fetch_system()
        cls.fetch_items()
        cls.fetch_common()
        cls.fetch_maps()
        cls.fetch_quests()

        # cls.fetch_special_words()
        cls.fetch_map_names()
        logger.info("===== ALL FILES FETCHED DONE.")

    @staticmethod
    def fetch_system():
        with open(DIR_ROOT / RAW_FILES["system"], "r", encoding="utf-8") as fp:
            data: dict = json.load(fp)
        results = {
            "gameTitle": data["gameTitle"],
            "locale": data["locale"],
            "skillTypes": [_ for _ in data["skillTypes"]],
            "basic": [_ for _ in data["terms"]["basic"] if _],
            "commands": [_ for _ in data["terms"]["commands"] if _],
            "messages": [v for k, v in data["terms"]["messages"].items() if v],
            "params": [_ for _ in data["terms"]["params"] if _],
        }

        with open(DIR_FETCHES / RAW_FILES["system"], "w", encoding='utf-8') as fp:
            json.dump(results, fp, ensure_ascii=False, indent=2)

        logger.info("\t- SYSTEM FETCHED DONE.")

    @staticmethod
    def fetch_items():
        with open(DIR_ROOT / RAW_FILES["items"], "r", encoding="utf-8") as fp:
            data: list[dict] = json.load(fp)

        results = []
        for d in data:
            if not d:
                continue
            if not d["description"] and not d["name"]:
                continue

            item = ItemData(id=d["id"], description=d["description"], name=d["name"])
            results.append(item.__dict__)

        with open(DIR_FETCHES / RAW_FILES["items"], "w", encoding="utf-8") as fp:
            json.dump(results, fp, ensure_ascii=False, indent=2)
        logger.info("\t- ITEMS FETCHED DONE.")

    @staticmethod
    def fetch_common():
        with open(DIR_ROOT / RAW_FILES["common"], "r", encoding="utf-8") as fp:
            data: list[dict] = json.load(fp)

        results = []
        for d in data:
            if not d:
                continue
            if all(_ not in {lst["code"] for lst in d["list"]} for _ in CODES_NEEDED_TRANSLATION.values()):
                """不含要翻译的"""
                continue

            for code_data in d["list"]:
                if code_data["code"] not in CODES_NEEDED_TRANSLATION.values():
                    continue

                if code_data["code"] == CODES_NEEDED_TRANSLATION["对话"]:
                    code = EventCodeData(id=d["id"], code=code_data["code"], param=code_data["parameters"])
                elif code_data["code"] == CODES_NEEDED_TRANSLATION["选项"]:
                    code = EventCodeData(id=d["id"], code=code_data["code"], param=code_data["parameters"][0])
                else:
                    raise Exception("其它code类型")
                results.append(code.__dict__)


        with open(DIR_FETCHES / RAW_FILES["common"], "w", encoding="utf-8") as fp:
            json.dump(results, fp, ensure_ascii=False, indent=2)
        logger.info("\t- COMMON FETCHED DONE.")

    @staticmethod
    def fetch_maps():
        for i in range(1, MAPS_COUNT + 1):
            file_name = RAW_FILES["maps"].format(i)
            with open(DIR_ROOT / file_name, "r", encoding="utf-8") as fp:
                data = json.load(fp)

            results = []
            if not data:
                continue
            for evt in data["events"]:
                if not evt:
                    continue

                for pg in evt["pages"]:
                    if all(_ not in {lst["code"] for lst in pg["list"]} for _ in CODES_NEEDED_TRANSLATION.values()):
                        """不含要翻译的"""
                        continue

                    for code_data in pg["list"]:
                        if code_data["code"] not in CODES_NEEDED_TRANSLATION.values():
                            continue

                        if code_data["code"] == CODES_NEEDED_TRANSLATION["对话"]:
                            code = EventCodeData(id=evt["id"], code=code_data["code"], param=code_data["parameters"])
                        elif code_data["code"] == CODES_NEEDED_TRANSLATION["选项"]:
                            code = EventCodeData(id=evt["id"], code=code_data["code"], param=code_data["parameters"][0])
                        else:
                            raise Exception("其它code类型")
                        results.append(code.__dict__)

            if not results:
                continue
            with open(DIR_FETCHES / file_name, "w", encoding="utf-8") as fp:
                json.dump(results, fp, ensure_ascii=False, indent=2)
        logger.info(f"\t- MAPS FETCHED DONE.")

    @staticmethod
    def fetch_quests():
        """和其他文件格式不一样"""
        with open(FILE_QUESTS, "r", encoding="utf-8") as fp:
            lines = fp.readlines()

        results = []
        result = None
        flag = False
        for line in lines:
            line = line.strip()
            if not line:
                continue

            result = {
                "key": line,
                "original": line,
                "translation": ""
            }

            if line.startswith("<quest "):
                flag = True

            elif flag and line == "</quest>":
                flag = False

            elif flag and result not in results:
                results.append(result)

        with open(DIR_FETCHES / RAW_FILES["quests_json"], "w", encoding="utf-8") as fp:
            json.dump(results, fp, ensure_ascii=False, indent=2)
        logger.info("\t- QUESTS FETCHED DONE.")

    @staticmethod
    def fetch_special_words():
        names: set = {"Me <br>"}
        for file in os.listdir(DIR_FETCHES):
            if file in {RAW_FILES["items"], RAW_FILES["system"]}:
                continue
            with open(DIR_FETCHES / file, "r", encoding="utf-8") as fp:
                data = json.load(fp)

            for d in data:
                if "\\C" not in d["param"][0]:
                    continue
                name = re.findall(r"\\[cC]\[\d*]([a-zA-Z\s\.]*?)\\[Cc]\[\d*]", d["param"][0])
                if not name or not name[0] or name[0].strip() in {"and", "that", "the"}:
                    continue
                names.add(name[0])

        with open(DIR_SUPPORT / "special_words.json", "w", encoding="utf-8") as fp:
            json.dump({_: "" for _ in names}, fp, ensure_ascii=False, indent=2)
        logger.info("\t- NAMES FETCHED DONE.")

    @staticmethod
    def fetch_map_names():
        results = {}
        for i in range(1, MAPS_COUNT + 1):
            file_name = RAW_FILES["maps"].format(i)
            with open(DIR_ROOT / file_name, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            if not data or not data["displayName"]:
                continue
            results[file_name] = data["displayName"]

        with open(DIR_SUPPORT / "map_names.json", "w", encoding="utf-8") as fp:
            json.dump(results, fp, ensure_ascii=False, indent=2)
        logger.info(f"\t- MAP NAMES FETCHED DONE.")

    """ PRE PROCESS """
    @classmethod
    def pre_process_all(cls):
        logger.info("##### STARTING PRE PROCESSING ALL FILES...")
        for file in os.listdir(DIR_FETCHES):
            cls.pre_process_duplicate(file)
            # cls.pre_process_special_words(file)
            cls.pre_process_paratranz(file)
        logger.info("===== ALL FILES PRE PROCESSED DONE.")

    @staticmethod
    def pre_process_duplicate(file: str):
        results = {}
        if file in {RAW_FILES["items"]}:
            with open(DIR_FETCHES / file, "r", encoding="utf-8") as fp:
                data = json.load(fp)

            for d in data:
                if d["description"] and d["description"] not in results:
                    results[d["description"]] = ""
                if d["name"] and d["name"] not in results:
                    results[d["name"]] = ""

        elif file in {RAW_FILES["system"]}:
            with open(DIR_FETCHES / file, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            results["gameTitle"] = data["gameTitle"]
            results["locale"] = data["locale"]
            for bsc in data["basic"]:
                if bsc not in results:
                    results[bsc] = ""

            for cmd in data["commands"]:
                if cmd not in results:
                    results[cmd] = ""

            for prm in data["params"]:
                if prm not in results:
                    results[prm] = ""

        elif file in {RAW_FILES["quests_json"]}:
            with open(DIR_FETCHES / file, "r", encoding="utf-8") as fp:
                results = json.load(fp)

        else:
            with open(DIR_FETCHES / file, "r", encoding="utf-8") as fp:
                data = json.load(fp)

            for d in data:
                for param in d["param"]:
                    if param not in results:
                        results[param] = ""

            if not results:
                return

        with open(DIR_PROCESS / file, "w", encoding="utf-8") as fp:
            json.dump(results, fp, ensure_ascii=False, indent=2)

    @staticmethod
    def pre_process_special_words(file: str):
        try:
            with open(DIR_LOCALIZATIONS / "special_words.json", "r", encoding="utf-8") as fp:
                names: dict = json.load(fp)
        except FileNotFoundError as e:
            logger.error("special_words 文件尚未翻译！")
            raise

        with open(DIR_PROCESS / file, "r", encoding="utf-8") as fp:
            data = json.load(fp)

        for raw, target in data.items():
            if raw == "Me <br>":
                data[raw] = "我 <br>"
                continue

            if "\\C" not in raw:
                continue

            name = re.findall(r"\\C\[\d*]([a-zA-Z\s\.]*?)\\[Cc]\[\d*]", raw)
            if not name or not name[0] or name[0].strip() in {"and", "that", "the", "NEW"} or name[0].strip() not in names:
                continue
            data[raw] = raw.replace(name[0], names[name[0]])

        with open(DIR_PROCESS / file, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)

    @staticmethod
    def pre_process_paratranz(file: str):
        """处理成 paratranz 能看懂的文件"""
        with open(DIR_PROCESS / file, "r", encoding="utf-8") as fp:
            data: dict = json.load(fp)
        if file in {RAW_FILES["quests_json"]}:
            results = data
        else:
            results = [
                {"key": k, "original": k.replace(r"(\c[2]PREVIOUS\c[0])", "").replace(r"(\C[3]NEW\C[0])", ""), "translation": ""}
                for k in data
            ]

        with open(DIR_PARATRANZ / file, "w", encoding="utf-8") as fp:
            json.dump(results, fp, ensure_ascii=False)
        # logger.info("\t- TRANSFER TO PARATRANZ FORMAT PRE PROCESSED DONE.")

    """ POST PRECESS """
    @classmethod
    def post_process_all(cls):
        logger.info("##### STARTING POST PROCESSING ALL FILES...")
        # cls.post_process_translated()
        # cls.post_process_paratranz()
        logger.info("===== ALL FILES POST PROCESSED DONE.")

    @staticmethod
    def post_process_translated():
        for file in os.listdir(DIR_PROCESS):
            if file in os.listdir(DIR_LOCALIZATIONS_FILES):
                os.remove(DIR_PROCESS / file)
        logger.info("\t- ALREADY TRANSLATED POST PROCESSED DONE.")

    """ DOWNLOAD """
    @classmethod
    def download_from_paratranz(cls):
        logger.info("##### STARTING DOWNLOADING ALL FILES...")
        cls.trigger_export()
        cls.download_export()
        cls.unzip_export()
        cls.move_export()
        cls.update_local_paratranz()
        cls.reconf_export()
        logger.info("===== ALL FILES DOWNLOADED DONE")

    @classmethod
    def trigger_export(cls):
        url = f"{PARATRANZ_BASE_URL}/projects/{PARATRANZ_PROJECT_ID}/artifacts"
        httpx.post(url, headers=PARATRANZ_HEADERS)
        logger.info("\t- EXPORT TRIGGERED DONE")

    @classmethod
    def download_export(cls):
        url = f"{PARATRANZ_BASE_URL}/projects/{PARATRANZ_PROJECT_ID}/artifacts/download"
        content = httpx.get(url, headers=PARATRANZ_HEADERS, follow_redirects=True).content
        with open(DIR_DOWNLOAD / "download.zip", "wb") as fp:
            fp.write(content)
        logger.info("\t- EXPORT DOWNLOADED DONE")

    @classmethod
    def unzip_export(cls):
        with zipfile.ZipFile(DIR_DOWNLOAD / "download.zip") as zfp:
            zfp.extractall(DIR_DOWNLOAD)
        logger.info("\t- EXPORT UNZIPED DONE")

    @classmethod
    def move_export(cls):
        for file in os.listdir(DIR_DOWNLOAD / "utf8" / VERSION):
            shutil.move(DIR_DOWNLOAD / "utf8" / VERSION / file, DIR_LOCALIZATIONS_FILES / file)
        logger.info("\t- EXPORT MOVED DONE")

    @classmethod
    def update_local_paratranz(cls):
        """更新本地的字典"""
        for file in os.listdir(DIR_LOCALIZATIONS_FILES):
            if not (DIR_PARATRANZ / file).exists():
                shutil.copyfile(
                    DIR_LOCALIZATIONS_FILES / file,
                    DIR_PARATRANZ / file
                )
            else:
                with open(DIR_LOCALIZATIONS_FILES / file, "r", encoding="utf-8") as fp:
                    data_translated: list[dict] = json.load(fp)

                with open(DIR_PARATRANZ / file, "r", encoding="utf-8") as fp:
                    data_fetched_raw: list[dict] = json.load(fp)

                for item_translated in data_translated:
                    for idx, item_fetched_raw in enumerate(data_fetched_raw):
                        if item_fetched_raw["key"] == item_translated["key"] and item_translated["translation"] != "":
                            data_fetched_raw[idx] = item_translated

                with open(DIR_PARATRANZ / file, "w", encoding="utf-8") as fp:
                    json.dump(data_fetched_raw, fp, ensure_ascii=False)
            logger.info(f"\t\t- UPDATE {file} DONE")
        logger.info("\t- UPDATE LOCAL PARATRANZ DONE")

    @classmethod
    def reconf_export(cls):
        for file in os.listdir(DIR_LOCALIZATIONS_FILES):
            with open(DIR_LOCALIZATIONS_FILES / file, "r", encoding="utf-8") as fp:
                data_raw: list[dict] = json.load(fp)

            data = {
                _["key"]: _["translation"]
                for _ in data_raw
            }

            with open(DIR_LOCALIZATIONS_FILES / file, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False)
        logger.info("\t- EXPORT RECONFED DONE")

    """ APPLY """
    @classmethod
    def apply_all(cls):
        logger.info("##### STARTING APPLYING ALL FILES...")
        cls.apply_system()
        cls.apply_items()
        cls.apply_common()
        cls.apply_maps()
        cls.apply_quests()
        cls.apply_map_names()
        logger.info("===== ALL FILES APPLIED DONE.")
        
    @staticmethod
    def apply_system():
        with open(DIR_LOCALIZATIONS_FILES / RAW_FILES["system"], "r", encoding="utf-8") as fp:
            data_localized = json.load(fp)
        with open(DIR_RESULTS / RAW_FILES["system"], "r", encoding="utf-8") as fp:
            data = json.load(fp)

        data["gameTitle"] = data_localized["gameTitle"]
        data["locale"] = data_localized["locale"]

        for idx, d in enumerate(data["skillTypes"]):
            if not d:
                continue
            if not data_localized.get(d):
                continue
            data["skillTypes"][idx] = data_localized[d]


        for idx, d in enumerate(data["terms"]["basic"]):
            if not d:
                continue
            if not data_localized.get(d):
                continue
            data["terms"]["basic"][idx] = data_localized[d]

        for idx, d in enumerate(data["terms"]["commands"]):
            if not d:
                continue
            if not data_localized.get(d):
                continue
            data["terms"]["commands"][idx] = data_localized[d]

        for idx, d in enumerate(data["terms"]["params"]):
            if not d:
                continue
            if not data_localized.get(d):
                continue
            data["terms"]["params"][idx] = data_localized[d]

        for key, value in data["terms"]["messages"].items():
            if not value:
                continue
            if not data_localized.get(value):
                continue
            data["terms"]["messages"][key] = data_localized[value]

        with open(DIR_RESULTS / RAW_FILES["system"], "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False)
        logger.info("\t- SYSTEM APPLIED DONE.")

    @staticmethod
    def apply_items():
        with open(DIR_LOCALIZATIONS_FILES / RAW_FILES["items"], "r", encoding="utf-8") as fp:
            data_localized: dict = json.load(fp)

        with open(DIR_RESULTS / RAW_FILES["items"], "r", encoding="utf-8") as fp:
            data: list = json.load(fp)
        for idx, d in enumerate(data):
            if not d:
                continue
            if d["description"]:
                if not data_localized.get(d["description"]):
                    continue
                data[idx]["description"] = data_localized[d["description"]]
            if d["name"]:
                if not data_localized.get(d["name"]):
                    continue
                data[idx]["name"] = data_localized[d["name"]]

        with open(DIR_RESULTS / RAW_FILES["items"], "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False)
        logger.info("\t- ITEMS APPLIED DONE.")

    @staticmethod
    def apply_common():
        with open(DIR_LOCALIZATIONS_FILES / RAW_FILES["common"], "r", encoding="utf-8") as fp:
            data_localized: dict = json.load(fp)

        with open(DIR_RESULTS / RAW_FILES["common"], "r", encoding="utf-8") as fp:
            data: list = json.load(fp)

        for data_idx, d in enumerate(data):
            if not d:
                continue

            if all(_ not in {lst["code"] for lst in d["list"]} for _ in CODES_NEEDED_TRANSLATION.values()):
                """不含要翻译的"""
                continue

            for list_idx, code in enumerate(d["list"]):
                if code["code"] not in CODES_NEEDED_TRANSLATION.values():
                    continue

                if code["code"] == CODES_NEEDED_TRANSLATION["对话"]:
                    key = code["parameters"][0]
                    try:
                        if not data_localized[key]:
                            continue
                        data[data_idx]["list"][list_idx]["parameters"][0] = data_localized[key]
                    except KeyError:
                        continue
                elif code["code"] == CODES_NEEDED_TRANSLATION["选项"]:
                    for code_idx, key in enumerate(code["parameters"][0]):
                        try:
                            if not data_localized[key]:
                                continue
                            data[data_idx]["list"][list_idx]["parameters"][0][code_idx] = data_localized[key]
                        except KeyError:
                            continue
                else:
                    raise Exception("其它code情况")

        with open(DIR_RESULTS / RAW_FILES["common"], "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False)
        logger.info("\t- COMMON APPLIED DONE.")

    @staticmethod
    def apply_maps():
        for i in range(1, MAPS_COUNT + 1):
            replace_needed = True if i == 37 else False

            file_name = RAW_FILES["maps"].format(i)
            if file_name not in os.listdir(DIR_LOCALIZATIONS_FILES):
                continue

            """汉化词典·"""
            with open(DIR_LOCALIZATIONS_FILES / file_name, "r", encoding="utf-8") as fp:
                data_localized: dict = json.load(fp)
            data_localized = {k.strip(): v.strip() for k, v in data_localized.items()}

            """提取词典"""
            with open(DIR_RESULTS / file_name, "r", encoding="utf-8") as fp:
                data_raw: dict = json.load(fp)
            if not data_raw:
                continue

            for evt_idx, evt in enumerate(data_raw["events"]):
                if not evt:
                    continue
                for pg_idx, pg in enumerate(evt["pages"]):
                    if all(_ not in {lst["code"] for lst in pg["list"]} for _ in CODES_NEEDED_TRANSLATION.values()):
                        """不含要翻译的"""
                        continue
                    for list_idx, code in enumerate(pg["list"]):
                        if code["code"] not in CODES_NEEDED_TRANSLATION.values():
                            continue

                        if code["code"] == CODES_NEEDED_TRANSLATION["对话"]:
                            key = code["parameters"][0].strip()
                            # if replace_needed:
                            #     key = key.replace("(\\C[3]NEW\\C[0]) ", "")  # 替换两个老是更新的东西
                            #     key = key.replace("(\\c[2]PREVIOUS\\c[0]) ", "")  # 替换两个老是更新的东西
                            #     key = key.replace("(\\C[3]NEW\\C[0])", "")  # 替换两个老是更新的东西
                            #     key = key.replace("(\\c[2]PREVIOUS\\c[0])", "")  # 替换两个老是更新的东西
                            try:
                                if not data_localized[key]:
                                    continue
                                if replace_needed:
                                    data_raw["events"][evt_idx]["pages"][pg_idx]["list"][list_idx]["parameters"][0] = data_localized[key]
                                else:
                                    data_raw["events"][evt_idx]["pages"][pg_idx]["list"][list_idx]["parameters"][0] = insert_linebreak_text(data_localized[key])
                            except KeyError:
                                continue
                        elif code["code"] == CODES_NEEDED_TRANSLATION["选项"]:
                            for code_idx, key in enumerate(code["parameters"][0]):
                                try:
                                    if not data_localized[key]:
                                        continue
                                    if replace_needed:
                                        data_raw["events"][evt_idx]["pages"][pg_idx]["list"][list_idx]["parameters"][0][code_idx] = data_localized[key]
                                    else:
                                        data_raw["events"][evt_idx]["pages"][pg_idx]["list"][list_idx]["parameters"][0][code_idx] = insert_linebreak_text(data_localized[key])
                                except KeyError:
                                    continue

                        else:
                            raise Exception("其它code情况")

            with open(DIR_RESULTS / file_name, "w", encoding="utf-8") as fp:
                json.dump(data_raw, fp, ensure_ascii=False)
        logger.info("\t- MAPS APPLIED DONE.")

    @staticmethod
    def apply_quests():
        with open(DIR_LOCALIZATIONS_FILES / RAW_FILES["quests_json"], "r", encoding="utf-8") as fp:
            data_localized: dict = json.load(fp)

        with open(DIR_RESULTS / RAW_FILES["quests"], "r", encoding="utf-8") as fp:
            lines = fp.readlines()

        for key, value in data_localized.items():
            if key.startswith("<quest") or key.startswith("</quest"):
                continue

            for idx, line in enumerate(lines):
                if line.strip() == key:
                    # lines[idx] = insert_linebreak_text(line.replace(key, value), "\n", 37)
                    lines[idx] = line.replace(key, value)

        with open(DIR_RESULTS / RAW_FILES["quests"], "w", encoding="utf-8") as fp:
            fp.writelines(lines)
        logger.info("\t- QUESTS APPLIED DONE.")

    @staticmethod
    def apply_map_names():
        try:
            with open(DIR_LOCALIZATIONS / "map_names.json", "r", encoding="utf-8") as fp:
                names: dict = json.load(fp)
        except FileNotFoundError as e:
            logger.error("map_names 文件尚未翻译！")
            raise

        for file_name, map_name in names.items():
            with open(DIR_RESULTS / file_name, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            if not data or not data["displayName"]:
                continue
            data["displayName"] = map_name
            with open(DIR_RESULTS / file_name, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False)
        logger.info("\t- MAP NAMES APPLIED DONE.")

    """ COVER """
    @staticmethod
    def cover_all():
        for file in os.listdir(DIR_RESULTS):
            if file == RAW_FILES["quests"]:
                shutil.copyfile(DIR_RESULTS / file, FILE_QUESTS)
                continue
            shutil.copyfile(DIR_RESULTS / file, DIR_ROOT / file)
        logger.info("***** ALL FILES COVERED DONE.")

    """ DROP """
    @staticmethod
    def drop_all():
        shutil.rmtree(DIR_FETCHES, ignore_errors=True)
        shutil.rmtree(DIR_PROCESS, ignore_errors=True)
        shutil.rmtree(DIR_SUPPORT, ignore_errors=True)
        shutil.rmtree(DIR_RESULTS, ignore_errors=True)
        logger.info("***** ALL FETCHES DROPPED DONE.")

    """ MISC """
    @staticmethod
    def count_length():
        logger.info("##### STARTING LENGTH COUNTING...")
        results = {}
        for file in os.listdir(DIR_PROCESS):
            with open(DIR_PROCESS / file, "r", encoding="utf-8") as fp:
                data = json.load(fp)
            results[file.split(".")[0]] = len(data)

        results = dict(sorted(results.items(), key=lambda _: _[1]))
        with open(DIR_SUPPORT / "count_length.json", "w", encoding="utf-8") as fp:
            json.dump(results, fp, ensure_ascii=False, indent=2)
        logger.info("===== LENGTH COUNTED DONE.")


def main():
    tr = Translation()
    tr.drop_all()           # 清除全部
    tr.init_dirs()          # 创建目录
    tr.fetch_all()          # 获取原文
    tr.pre_process_all()    # 预处理(合并重复句子、替换专有名词)
    tr.post_process_all()   # 后处理(删除已翻译的)
    tr.download_from_paratranz()    # 从 Paratranz 下载
    tr.apply_all()          # 应用翻译
    tr.count_length()       # 统计内容长度
    tr.cover_all()          # 覆盖源文件

    subprocess.Popen(f'"{DIR_ROOT.parent.parent / "Game.exe"}"')


if __name__ == '__main__':
    main()
