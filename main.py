import json
import os
import shutil
import re

from consts import *
from models import *
from log import *


class Translation:
    def __init__(self):
        ...

    @classmethod
    def init_dirs(cls):
        os.makedirs(DIR_FETCHES, exist_ok=True)
        os.makedirs(DIR_SUPPORT, exist_ok=True)
        os.makedirs(DIR_PROCESS, exist_ok=True)
        os.makedirs(DIR_MACHINE, exist_ok=True)
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
        cls.fetch_special_words()
        cls.fetch_map_names()
        logger.info("===== ALL FILES FETCHED DONE.")

    @staticmethod
    def fetch_system():
        with open(DIR_ROOT / RAW_FILES["system"], "r", encoding="utf-8") as fp:
            data: dict = json.load(fp)
        results = {
            "gameTitle": data["gameTitle"],
            "locale": data["locale"],
            "commands": [_ for _ in data["terms"]["commands"] if _]
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
            cls.pre_process_special_words(file)
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
            for cmd in data["commands"]:
                if cmd not in results:
                    results[cmd] = ""

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

    """ POST PRECESS """
    @classmethod
    def post_process_all(cls):
        logger.info("##### STARTING POST PROCESSING ALL FILES...")
        cls.post_process_translated()
        cls.post_process_machine()
        logger.info("===== ALL FILES POST PROCESSED DONE.")

    @staticmethod
    def post_process_translated():
        for file in os.listdir(DIR_PROCESS):
            if file in os.listdir(DIR_LOCALIZATIONS_FILES):
                os.remove(DIR_PROCESS / file)
        logger.info("\t- ALREADY TRANSLATED POST PROCESSED DONE.")

    @staticmethod
    def post_process_machine():
        for file in os.listdir(DIR_PROCESS):
            file_name = file.split(".")[0]
            with open(DIR_PROCESS / file, "r", encoding="utf-8") as fp:
                data: dict = json.load(fp)

            with open(DIR_MACHINE / "from" / f"{file_name}.txt", "w", encoding="utf-8") as fp:
                fp.write("\n".join(list(data.keys())))
        logger.info("\t- TRANSFER TO TXT POST PROCESSED DONE.")

    """ APPLY """
    @classmethod
    def apply_all(cls):
        logger.info("##### STARTING APPLYING ALL FILES...")
        cls.apply_system()
        cls.apply_items()
        cls.apply_common()
        cls.apply_maps()
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

        for idx, d in enumerate(data["terms"]["commands"]):
            if not d:
                continue
            data["terms"]["commands"][idx] = data_localized[d]

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
                data[idx]["description"] = data_localized[d["description"]]
            if d["name"]:
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
            file_name = RAW_FILES["maps"].format(i)
            if file_name not in os.listdir(DIR_LOCALIZATIONS_FILES):
                continue
            with open(DIR_LOCALIZATIONS_FILES / file_name, "r", encoding="utf-8") as fp:
                data_localized: dict = json.load(fp)
            with open(DIR_RESULTS / file_name, "r", encoding="utf-8") as fp:
                data: dict = json.load(fp)
            if not data:
                continue

            for evt_idx, evt in enumerate(data["events"]):
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
                            key = code["parameters"][0]
                            try:
                                if not data_localized[key]:
                                    continue
                                data["events"][evt_idx]["pages"][pg_idx]["list"][list_idx]["parameters"][0] = data_localized[key]
                            except KeyError:
                                continue
                        elif code["code"] == CODES_NEEDED_TRANSLATION["选项"]:
                            for code_idx, key in enumerate(code["parameters"][0]):
                                try:
                                    if not data_localized[key]:
                                        continue
                                    data["events"][evt_idx]["pages"][pg_idx]["list"][list_idx]["parameters"][0][code_idx] = data_localized[key]
                                except KeyError:
                                    continue

                        else:
                            raise Exception("其它code情况")

            with open(DIR_RESULTS / file_name, "w", encoding="utf-8") as fp:
                json.dump(data, fp, ensure_ascii=False)
        logger.info("\t- MAPS APPLIED DONE.")

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
    tr.apply_all()          # 应用翻译
    tr.count_length()       # 统计内容长度
    tr.cover_all()          # 覆盖源文件


if __name__ == '__main__':
    main()
