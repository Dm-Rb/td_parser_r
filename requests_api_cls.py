import requests
import math
import requests_body
from parsing_response_cls import Parsing

class RequestToAPI:
    API_URL = 'https://webservice.tecalliance.services/pegasus-3-0/services/TecdocToCatDLW.jsonEndpoint'

    @classmethod
    def __init__(cls, headers, current_brand):
        cls.headers = headers
        cls.current_brand = current_brand
        cls.car_manufacturers = cls.get_car_manufacturers()
        cls.brands_response = cls.get_brands()
        cls.brands = cls.get_brandName_brandId()
        cls.groups = cls.get_groups_name_id_cont()

    @classmethod
    def get_car_manufacturers(cls):
        print('RequestToAPI > get_car_manufacturers')
        body_request = requests_body.get_car_manufacturers
        response = requests.post(url=cls.API_URL, headers=cls.headers, json=body_request)
        response_json = response.json()
        if response_json["data"]["array"]:
            car_manufacturers = [{"name": i["manuName"], 'id': i["manuId"]} for i in response_json["data"]["array"]]
            return car_manufacturers
        else:
            raise ValueError('Не удалось получить ответ > get_car_manufacturers')


    @classmethod
    def get_brands(cls):
        print('RequestToAPI > get_brands')
        body_request = requests_body.get_brands

        response = requests.post(url=cls.API_URL, headers=cls.headers, json=body_request)
        return response.json()

    @classmethod
    def get_brandName_brandId(cls):
        # {название бренда: ид бренда}
        print('RequestToAPI > get_brandName_brandId')

        if cls.brands_response:
            brand_idbrand = []
            for obj in cls.brands_response['dataSupplierFacets']['counts']:
                brand_idbrand.append({'brand_name': obj['mfrName'], 'brand_id': obj['dataSupplierId']})

                if obj['mfrName'] == cls.current_brand:
                    # переназначаем атрибут класса со строки на ключ с парой имя, ИД
                    cls.current_brand = {'brand_name': obj['mfrName'], 'brand_id': obj['dataSupplierId']}

            return brand_idbrand

    @classmethod
    def get_groups_name_id_cont(cls):
        # выбираем все группы относительно current_brand

        print('RequestToAPI > get_nameGroups_idGroups')
        body_request = requests_body.get_nameGroups_idGroups
        # добавляем ИД бренда в тело
        body_request["getArticles"]["arg0"]["dataSupplierIds"] = cls.current_brand['brand_id']

        if cls.brands:
            response = requests.post(url=cls.API_URL, headers=cls.headers, json=body_request)
            response_json = response.json()
            namebrands_idbrands = []
            for elem in response_json['genericArticleFacets']['counts']:
                namebrands_idbrands.append(
                    {'group_name': elem["genericArticleDescription"], 'group_id': elem["genericArticleId"], 'group_count': elem['count']}
                )
            return namebrands_idbrands
        else:
            raise ValueError('namebrands_idbrands is empty')

    @classmethod
    def get_articles_list(cls, brand_id, group_id, group_count):
        # получаем список артикулов относительно бренда и группы
        # пара имя артикула: ИД артикула

        print('RequestToAPI > get_articles_list')
        body_request = requests_body.get_articles_list

        body_request["getArticles"]["arg0"]["dataSupplierIds"] = brand_id
        body_request["getArticles"]["arg0"]["genericArticleIds"] = group_id
        response_list = []
        if group_count >= 1000:
            body_request["getArticles"]["arg0"]["perPage"] = 1000
            for page in range(1, math.ceil(group_count / 1000) + 1):
                body_request["getArticles"]["arg0"]["page"] = page
                response = requests.post(url=cls.API_URL, headers=cls.headers, json=body_request)
                response_json = response.json()
                response_list.extend(response_json['articles'])

        else:
            body_request["getArticles"]["arg0"]["perPage"] = group_count
            body_request["getArticles"]["arg0"]["page"] = 1
            response = requests.post(url=cls.API_URL, headers=cls.headers, json=body_request)
            response_json = response.json()
            response_list.extend(response_json['articles'])

        articles = []
        for elem in response_list:
            article_name = elem['articleNumber']
            article_id = [i["legacyArticleId"] for i in elem["genericArticles"]]
            if len(article_id) > 1:
                raise ValueError(f'{article_name} : len(article_id) > 1')
            articles.append({'article_name': article_name, 'article_id': article_id[0]})

        return articles

    @classmethod
    def get_article_details(cls, brand_id, group_id, article_name):
        body_request = requests_body.get_article_details
        body_request["getArticles"]["arg0"]["searchQuery"] = article_name
        body_request["getArticles"]["arg0"]["dataSupplierIds"] = brand_id
        body_request["getArticles"]["arg0"]["genericArticleIds"] = group_id
        response = requests.post(url=cls.API_URL, headers=cls.headers, json=body_request)

        return response.json()


    @classmethod
    def get_related_vehicles(cls, article_id):
        # возвращает список id-car_tecdoc

        body_request = requests_body.get_related_vehicles
        body_request["getArticleLinkedAllLinkingTargetManufacturer2"]["arg0"]["articleId"] = article_id

        response = requests.post(url=cls.API_URL, headers=cls.headers, json=body_request)
        response_js = response.json()
        if response_js['data']:
            cars_id = []
            for iter_elem in response_js['data']["array"]:
                related_vehicle_response_json = cls.get_vehicle_id(article_id=article_id, manu_id=iter_elem['manuId'])
                for array_1 in related_vehicle_response_json["data"]['array']:
                    for array_2 in array_1["articleLinkages"]['array']:
                        cars_id.append(array_2['linkingTargetId'])

            cars_id = list(set(cars_id))
            return cars_id
        else:
            return None

    @classmethod
    def get_vehicle_id(cls, article_id, manu_id):
        # вспомогательная функция для get_related_vehicles
        body_request = requests_body.get_vehicle_id
        body_request["getArticleLinkedAllLinkingTarget4"]["arg0"]["articleId"] = article_id
        body_request["getArticleLinkedAllLinkingTarget4"]["arg0"]["linkingTargetManuId"] = manu_id
        response = requests.post(url=cls.API_URL, headers=cls.headers, json=body_request)

        return response.json()

    @classmethod
    def get_car_details(cls, vehicle_id):
        print('RequestToAPI > get_car_details')
        body_request = requests_body.get_car_details
        body_request["getLinkageTargets"]["arg0"]["linkageTargetIds"] = [{"type": "P", "id": f'{vehicle_id}'}, {"type": "O", "id": f'{vehicle_id}'}]

        response = requests.post(url=cls.API_URL, headers=cls.headers, json=body_request)
        response_json_modification = response.json()  # ответ содержит детальную информацию авто
        if response_json_modification['linkageTargets']:
            manufacture_name = response_json_modification['linkageTargets'][0]["mfrName"]
            # Получить детали о серии текущей модификации
            manuf_id = int
            for manuf in cls.car_manufacturers:
                if manuf['name'] == manufacture_name:
                    manuf_id = manuf['id']
                    break
            body_request = requests_body.get_car_series
            body_request["getLinkageTargets"]["arg0"]["mfrIds"] = [manuf_id]
            response = requests.post(url=cls.API_URL, headers=cls.headers, json=body_request)
            response_json_series = response.json()  # ответ содержит информацию о всех сериях авто
            if response_json_series["vehicleModelSeriesFacets"]["counts"]:
                obj = cls.create_obj_new_car(response_json_modification, response_json_series)
                return obj
            else:
                raise ValueError('Ответ не содержит данных ["vehicleModelSeriesFacets"]["counts"] ')
        else:
            raise ValueError("Ответ не содержит данных 'linkageTargets'")

    @staticmethod
    def create_obj_new_car(r_modfic, r_series):

        manufacture_name = r_modfic['linkageTargets'][0]["mfrName"]
        model_series_name = r_modfic['linkageTargets'][0]["vehicleModelSeriesName"]
        types = {"L": "cv", "B": "mb", "V": "pc"}
        type = types[r_modfic['linkageTargets'][0]["subLinkageTargetType"]]
        range_seria = str
        for seria in r_series["vehicleModelSeriesFacets"]["counts"]:
            if seria["name"] == model_series_name:
                range_seria_begin = str(seria["beginYearMonth"])[4:] + '.' + str(seria["beginYearMonth"])[:4]
                range_seria_end = str(seria["endYearMonth"])[4:] + '.' + str(seria["endYearMonth"])[:4]
                range_seria = range_seria_begin + ' - ' + range_seria_end
                break

        car_obj = {
            "manufacturer": manufacture_name,
            "name": model_series_name,
            "range": range_seria,
            "mod_type": type
        }

        r_modfic_data = r_modfic['linkageTargets'][0]
        range_begin = r_modfic_data["beginYearMonth"][5:] + '.' + r_modfic_data["beginYearMonth"][:4]
        range_end = r_modfic_data["endYearMonth"][5:] + '.' + r_modfic_data["endYearMonth"][:4]

        modification = {'name': r_modfic_data["description"],
                        'range': range_begin + ' - ' + range_end
                        }

        if r_modfic_data.get("kiloWattsTo", '') != '':
            modification["kwt"] = r_modfic_data["kiloWattsTo"]
        if r_modfic_data.get("horsePowerTo", '') != '':
            modification["hp"] = r_modfic_data["horsePowerTo"]
        if r_modfic_data.get("capacityCC", '') != '':
            modification["ccm"] = r_modfic_data["capacityCC"]
        if r_modfic_data.get("bodyStyle", '') != '':
            modification["body"] = r_modfic_data["bodyStyle"]
        if r_modfic_data.get("cylinders", '') != '':
            modification["cylinders"] = r_modfic_data["cylinders"]
        if r_modfic_data.get("valves", '') != '':
            modification["valves"] = r_modfic_data["valves"]
        if r_modfic_data.get("engineType", '') != '':
            modification["engine"] = r_modfic_data["engineType"]
        if r_modfic_data.get("driveType", '') != '':
            modification["drive"] = r_modfic_data["driveType"]
        if r_modfic_data.get("fuelType", '') != '':
            modification["fuel"] = r_modfic_data["fuelType"]
        if r_modfic_data.get("fuelMixtureFormationType", '') != '':
            modification["fuel_supply"] = r_modfic_data["fuelMixtureFormationType"]
        if r_modfic_data.get("engines", '') != '':
            if len(r_modfic_data) > 1:
                modification["engine_code"] = ', '.join([i["code"] for i in r_modfic_data["engines"]])
            else:
                modification["engine_code"] = r_modfic_data["engines"][0]["code"]
        car_obj["modifications"] = [modification]

        return car_obj











