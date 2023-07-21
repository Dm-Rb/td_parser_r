from browser import get_headers
from config import ConfigParsing
from requests_api_cls import RequestToAPI
from parsing_response_cls import Parsing
from tracking_cls import Tracking


def main():
    # create obj's
    RequestToAPI(headers=get_headers(), current_brand=ConfigParsing.brand)
    parsing = Parsing()
    groups = RequestToAPI.groups

    for group_i in range(Tracking.last_group(), len(groups)):
        Tracking.get_group(group_i)  # запись в треккинг текущей группы
        print(f"Обход раздела: {RequestToAPI.current_brand['brand_name']}, {groups[group_i]['group_name']}")
        # articles = [{'article_name': str(v), 'article_id': int(v)}, {...}, ...]
        articles = RequestToAPI.get_articles_list(brand_id=RequestToAPI.current_brand['brand_id'],
                                                       group_id=groups[group_i]["group_id"],
                                                       group_count=groups[group_i]['group_count']
                                                    )

        print(f"Обход раздела: {RequestToAPI.current_brand['brand_name']}, {groups[group_i]['group_name']}({len(articles)})")
        for article_i in range(Tracking.last_article(), len(articles)):
            Tracking.get_article(article_i)

            # ответ по конкретному артикулу
            article_detail = RequestToAPI.get_article_details(brand_id=RequestToAPI.current_brand['brand_id'],
                                                               group_id=groups[group_i]["group_id"],
                                                               article_name=articles[article_i]['article_name']
                                                               )
            if article_detail["status"] != 200:
                raise ValueError('article_detail -> response status_code != 200')
            # ответ по связанным ТС с конкретным артикулом, список tecdoc_id_car
            related_vehicles_id = RequestToAPI.get_related_vehicles(articles[article_i]['article_id'])
            # сгенерировать итоговый объект по текущему артикулу
            parsing.create_obj_article(article_detail, related_vehicles_id)

        # очистить поле current_article
        Tracking.clear_article()
    print("Готово")




