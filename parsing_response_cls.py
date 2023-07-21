import os
import requests
import base64
from config import ConfigParsing
from tracking_cls import Tracking
import sqlite3
import ast
import json
from requests_api_cls import RequestToAPI

class Parsing:

    PATH_TO_SAVE_FOLDER = None
    STRUCTURE = {
        "version": "td",
        "items": []
        }
    COUNT_ITEMS = 300

    def __init__(self):
        self.data_w_to_file = self.STRUCTURE
        self.connection = sqlite3.connect(ConfigParsing.path_to_db)
        self.cursor = self.connection.cursor()

    # Метод базы данных
    def get_car_details(self, tecdoc_id):
        with self.connection:
            result = self.cursor.execute(f"SELECT data FROM 'cars' WHERE tecdoc_id = ?", (tecdoc_id,)).fetchmany(1)
            if bool(result):
                return result[0][0]

    def add_new_car(self, tecdoc_id, data):
        """ Добавить новую строку """
        data_str = str(data)

        with self.connection:
            return self.cursor.execute(
                "INSERT INTO 'cars' ('tecdoc_id', 'tecdoc_id') VALUES(?, ?)",
                (tecdoc_id, data_str,))

    # Разбор ответа json
    def parse_response(self, response_article_detail):
        result_obj = {}

        if response_article_detail:
            if len(response_article_detail["articles"]) > 1:
                raise ValueError('response_article_detail["articles"]) > 1')

            array = response_article_detail["articles"][0]
            result_obj["brand"] = array["mfrName"]

            if len(array["genericArticles"]) > 1:
                raise ValueError('len(arrow["genericArticles"]) > 1, в ответе более одной товарной группы')
            result_obj["name"] = array["genericArticles"][0]["genericArticleDescription"]
            result_obj["group"] = array["genericArticles"][0]["genericArticleDescription"]
            result_obj["article"] = array["articleNumber"]
            print(result_obj["article"], end=' ')
            result_obj["catalog"] = "Автозапчасти"

            if array["articleText"]:
                result_obj["text"] = ''
                for elem in array["articleText"]:
                    text = f'{elem["text"] }'
                    result_obj["text"] += text

            if array["gtins"]:
                if len(array["gtins"]) > 1:
                    result_obj["barcode"] = ', '.join(array["gtins"])
                else:
                    result_obj["barcode"] = array["gtins"][0]

            if array["misc"].get("quantityPerPackage", '') != '':
                result_obj["unit"] = array["misc"]["quantityPerPackage"]

            if array["misc"].get("quantityPerPartPerPackage", "") != '':
                result_obj["pack"] = array["misc"]["quantityPerPartPerPackage"]

            if array["misc"].get("articleStatusDescription", '') != '':
                result_obj["status"] = array["misc"]["articleStatusDescription"]
            if array["tradeNumbers"]:
                result_obj["spares"] = array["tradeNumbers"]

            # -- make asyncio

            if array["images"]:
                result_obj["files"] = []
                for elem in array["images"]:
                    # if elem.get('imageURL3200', '') != '':
                    #     data = self.get_img_convert_base64(url=elem['imageURL3200'])
                    #     result_obj["files"].append(data)
                    if elem.get('imageURL1600', '') != '':
                        data = self.get_img_convert_base64(url=elem['imageURL1600'])
                        result_obj["files"].append(data)
                    elif elem.get('imageURL800', '') != '':
                        data = self.get_img_convert_base64(url=elem['imageURL800'])
                        result_obj["files"].append(data)

            if array["pdfs"]:
                if result_obj.get("files", '') == '':
                    result_obj["files"] = []
                for elem in array["pdfs"]:
                    data = self.get_img_convert_base64(url=elem["url"])
                    result_obj["files"].append(data)
            # --

            if array["articleCriteria"]:
                result_obj["params"] = []
                for elem in array["articleCriteria"]:
                    if elem["criteriaDescription"]:
                        if result_obj["params"]:
                            flag = True
                            for i in range(len(result_obj["params"])):
                                if result_obj["params"][i]['name'] == elem["criteriaDescription"]:
                                    # добавтить по второе значение по эквивалентному кллючу
                                    result_obj["params"][i]["value"] = str(result_obj["params"][i]["value"].replace('\\', '')) + ', ' + elem[
                                        "formattedValue"].replace('\\', '')
                                    flag = False
                                    break
                            if flag:
                                result_obj["params"].append({'name': elem["criteriaDescription"].replace('\\', ''),
                                               "value": elem["formattedValue"].replace('\\', '')})
                        else:
                            result_obj["params"].append({'name': elem["criteriaDescription"].replace('\\', ''),
                                           "value": elem["formattedValue"].replace('\\', '')})

            if array["oemNumbers"]:
                result_obj['analogs'] = []
                for elem in array["oemNumbers"]:
                    if result_obj['analogs']:
                        flag = True
                        for i in range(len(result_obj['analogs'])):
                            if elem["mfrName"] in result_obj['analogs'][i].keys():
                                result_obj['analogs'][i][elem["mfrName"]].append(elem["articleNumber"])
                                flag = False
                                break
                        if flag:
                            result_obj['analogs'].append({elem["mfrName"]: [elem["articleNumber"]]})
                    else:
                        result_obj['analogs'].append({elem["mfrName"]: [elem["articleNumber"]]})

            if array["partsList"]:
                result_obj["components"] = []
                for elem in array["partsList"]:
                    result_obj["components"].append({"article": elem["articleNumber"], "quantity": elem["quantity"]})
            print('-ok')
        else:
            print('response_article_detail - NONE')

        return result_obj

    def get_car_detais(self, related_vehicles_id):
        # related_vehicles_id = [int, int, ...]
        # Принимает список номеров текдок авто, обращается к базе данных для получания деталей по каждому авто
        models_list = []

        for key in related_vehicles_id:

            result_db = self.get_car_details(key)
            if result_db:
                model = ast.literal_eval(result_db)
            else:
                print(f'Авто с ключом {key} отсутствует в базе данных, поиск на сайте и добавление в БД')
                model = RequestToAPI.get_car_details(key)
                self.add_new_car(key, model)



            if len(model['modifications']) > 1:
                print(model)
                raise ValueError("len(obj['modifications']) > 1:")
            models_list.append(model)

        validate_list = self.validate_cars(models_list, related_vehicles_id)

        return validate_list

    def validate_cars(self, models_list, related_vehicles_id):
        # Валидирует детали авто под вгрузчик
        validate_models_list = []

        for model in models_list:
            if validate_models_list:
                flag = True #
                for i in range(len(validate_models_list)):
                    if validate_models_list[i]["manufacturer"] == model["manufacturer"]:
                        if validate_models_list[i]["name"] == model["name"] and validate_models_list[i]["range"] == model["range"]:
                            if validate_models_list[i]["mod_type"] == model["mod_type"]:
                                validate_models_list[i]['modifications'].append(model['modifications'][0])
                                flag = False
                                break
                if flag:
                    validate_models_list.append(model)
            else:
                validate_models_list.append(model)
        # # Check
        # count = 0
        # for i in range(len(validate_models_list)):
        #     count += len(validate_models_list[i]['modifications'])
        # if len(related_vehicles_id) != count:
        #     print(validate_models_list)
        #     raise ValueError('len(related_vehicles_id) != count')

        return validate_models_list

    @staticmethod
    def get_img_convert_base64(url):
            r = requests.get(url)
            if r.status_code == 200:
                encoded_string = base64.b64encode(r.content)
                return str(encoded_string).lstrip("b'").rstrip("'")

    def create_obj_article(self, article_detail, related_vehicles_id):
        # Собирает данные из article_detail и elated_vehicles_id в единую структуру
        details = self.parse_response(article_detail)

        # if related_vehicles_id != None
        if related_vehicles_id:
            print('related vehicles', end=' ')
            related_vehicles = self.get_car_detais(related_vehicles_id)
            details["models"] = related_vehicles
            print('-ok')
        else:
            print('related vehicles - None')

        self.data_w_to_file["items"].append(details)

        if len(self.data_w_to_file["items"]) >= self.COUNT_ITEMS:
            # записать данные в файл и обновить атрибут
            self.save_to_file(data=self.data_w_to_file)
            self.data_w_to_file["items"].clear()

    @staticmethod
    def save_to_file(data):
        dir_path = os.path.join(ConfigParsing.path_dir_to_save, ConfigParsing.brand)

        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)
        files = os.listdir(dir_path)
        files = list(filter(lambda x: x.endswith('.json'), files))
        new_file_name = ConfigParsing.brand + '_' + str(len(files) + 1) + '.json'
        print(f"> save_to_file > {new_file_name}")
        with open(os.path.join(dir_path, new_file_name), 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
        Tracking.save()







