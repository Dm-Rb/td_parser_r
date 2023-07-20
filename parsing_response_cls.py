import json
import os
import requests
import base64
from config import ConfigParsing
from tracking_cls import Tracking


class Parsing:

    PATH_TO_SAVE_FOLDER = None
    PATH_TO_FILE_cars_hash = 'cars_hash.json' #os.path.join('.', 'cars_hash.json')
    STRUCTURE = {
        "version": "td",
        "items": []
        }
    COUNT_ITEMS = 20

    def __init__(self):
        self.data_w_to_file = self.STRUCTURE
        self.cars_hash = self.get_cars_hash_from_jsonfile()  # вот тут мутная херня

    def get_cars_hash_from_jsonfile(self):
        with open(self.PATH_TO_FILE_cars_hash, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

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

            if array["misc"]["quantityPerPackage"]:
                result_obj["unit"] = array["misc"]["quantityPerPackage"]

            if array["misc"].get("quantityPerPartPerPackage", "") != '':
                result_obj["pack"] = array["misc"]["quantityPerPartPerPackage"]

            if array["misc"]["articleStatusDescription"]:
                result_obj["status"] = array["misc"]["articleStatusDescription"]
            if array["tradeNumbers"]:
                result_obj["spares"] = array["tradeNumbers"]

            # if array["images"]:
            #     result_obj["files"] = []
            #     for elem in array["images"]:
            #         # if elem.get('imageURL3200', '') != '':
            #         #     data = self.get_img_convert_base64(url=elem['imageURL3200'])
            #         #     result_obj["files"].append(data)
            #         if elem.get('imageURL1600', '') != '':
            #             data = self.get_img_convert_base64(url=elem['imageURL1600'])
            #             result_obj["files"].append(data)
            #         elif elem.get('imageURL800', '') != '':
            #             data = self.get_img_convert_base64(url=elem['imageURL800'])
            #             result_obj["files"].append(data)
            #
            # if array["pdfs"]:
            #     if result_obj.get("files", '') == '':
            #         result_obj["files"] = []
            #     for elem in array["pdfs"]:
            #         data = self.get_img_convert_base64(url=elem["url"])
            #         result_obj["files"].append(data)

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
        # формируем валидную структуру поля models на базе номеров текдок и файла cars_hash.json

        models_list = []
        # elem response_article_detail int -> str
        related_vehicles_id = [str(i) for i in related_vehicles_id]

        for key in related_vehicles_id:
            try:
                # ПРОБЛЕМА!!!!
                hash_table_cars = self.get_cars_hash_from_jsonfile()
                model = hash_table_cars[key]
            except KeyError:
                raise ValueError(f"Не найдено ТС по ключу -- {key} -- , необходимо добавить данные")

            if len(model['modifications']) > 1:
                print(model)
                raise ValueError("len(obj['modifications']) > 1:")
            models_list.append(model)

        validate_list = self.validate_cars(models_list)

        return validate_list

    def validate_cars(self, models_list):
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
        # собрать данные из article_detail и elated_vehicles_id в единую структуру
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
