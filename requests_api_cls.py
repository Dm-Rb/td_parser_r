import requests
import math
import requests_body

class RequestToAPI:
    API_URL = 'https://webservice.tecalliance.services/pegasus-3-0/services/TecdocToCatDLW.jsonEndpoint'

    def __init__(self, headers, current_brand):
        self.headers = headers
        self.current_brand = current_brand
        self.brands_response = self.get_brands()
        self.namebrands_idbrands = self.get_brandName_brandId()
        self.namegroups_idgroups = self.get_nameGroups_idGroups()
        self.articles_list = None

    def return_namebrands_idbrands(self):
        return self.namegroups_idgroups

    def get_brands(self):
        print('RequestToAPI > get_brands')
        body_request = requests_body.get_brands

        response = requests.post(url=self.API_URL, headers=self.headers, json=body_request)
        return response.json()

    def get_brandName_brandId(self):
        # {название бренда: ид бренда}
        print('RequestToAPI > get_brandName_brandId')

        if self.brands_response:
            brand_idbrand = []
            for obj in self.brands_response['dataSupplierFacets']['counts']:
                brand_idbrand.append({'brand_name': obj['mfrName'], 'brand_id': obj['dataSupplierId']})

                if obj['mfrName'] == self.current_brand:
                    # переназначаем атрибут класса со строки на ключ с парой имя, ИД
                    self.current_brand = {'brand_name': obj['mfrName'], 'brand_id': obj['dataSupplierId']}

            return brand_idbrand

    def get_nameGroups_idGroups(self):
        # выбираем все группы относительно current_brand

        print('RequestToAPI > get_nameGroups_idGroups')
        body_request = requests_body.get_nameGroups_idGroups
        # добавляем ИД бренда в тело
        body_request["getArticles"]["arg0"]["dataSupplierIds"] = self.current_brand['brand_id']

        if self.namebrands_idbrands:
            response = requests.post(url=self.API_URL, headers=self.headers, json=body_request)
            response_json = response.json()
            namebrands_idbrands = []
            for elem in response_json['genericArticleFacets']['counts']:
                namebrands_idbrands.append(
                    {'group_name': elem["genericArticleDescription"], 'group_id': elem["genericArticleId"], 'group_count': elem['count']}
                )
            return namebrands_idbrands
        else:
            raise ValueError('namebrands_idbrands is empty')

    def get_articles_list(self, brand_id, group_id, group_count):
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
                response = requests.post(url=self.API_URL, headers=self.headers, json=body_request)
                response_json = response.json()
                response_list.extend(response_json['articles'])

        else:
            body_request["getArticles"]["arg0"]["perPage"] = group_count
            body_request["getArticles"]["arg0"]["page"] = 1
            response = requests.post(url=self.API_URL, headers=self.headers, json=body_request)
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


    def get_article_details(self, brand_id, group_id, article_name):
        body_request = requests_body.get_article_details
        body_request["getArticles"]["arg0"]["searchQuery"] = article_name
        body_request["getArticles"]["arg0"]["dataSupplierIds"] = brand_id
        body_request["getArticles"]["arg0"]["genericArticleIds"] = group_id
        response = requests.post(url=self.API_URL, headers=self.headers, json=body_request)

        return response.json()

    def get_related_vehicles(self, article_id):
        # возвращает список id-car_tecdoc

        body_request = requests_body.get_related_vehicles
        body_request["getArticleLinkedAllLinkingTargetManufacturer2"]["arg0"]["articleId"] = article_id

        response = requests.post(url=self.API_URL, headers=self.headers, json=body_request)
        response_js = response.json()
        if response_js['data']:
            cars_id = []
            for iter_elem in response_js['data']["array"]:
                related_vehicle_response_json = self.get_vehicle_id(article_id=article_id, manu_id=iter_elem['manuId'])
                for array_1 in related_vehicle_response_json["data"]['array']:
                    for array_2 in array_1["articleLinkages"]['array']:
                        cars_id.append(array_2['linkingTargetId'])

            cars_id = list(set(cars_id))
            return cars_id
        else:
            return None

    def get_vehicle_id(self, article_id, manu_id):
        # вспомогательная функция для get_related_vehicles
        body_request = requests_body.get_vehicle_id
        body_request["getArticleLinkedAllLinkingTarget4"]["arg0"]["articleId"] = article_id
        body_request["getArticleLinkedAllLinkingTarget4"]["arg0"]["linkingTargetManuId"] = manu_id
        response = requests.post(url=self.API_URL, headers=self.headers, json=body_request)

        return response.json()






