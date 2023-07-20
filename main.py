from browser import get_headers
from config import ConfigParsing
from requests_api_cls import RequestToAPI
from parsing_response_cls import Parsing
from tracking_cls import Tracking

def main():
    headers = get_headers()

    # create obj's
    response_json = RequestToAPI(headers=headers, current_brand=ConfigParsing.brand)
    parsing = Parsing()
    # -- кульбиты с треккингом, есть данные -> вернуть срез, нет -> оставить список групп из ответа
    tracking_groups = Tracking.return_groups(lst=response_json.namegroups_idgroups)
    if tracking_groups:
        groups = tracking_groups
    else:
        groups = response_json.namegroups_idgroups
    # --
    for group in groups:
        Tracking.get_group(group)  # запись в треккинг текущей группы
        print(f"Обход раздела: {response_json.current_brand['brand_name']}, {group['group_name']}")
        # article_list = [{'article_name': str(v), 'article_id': int(v)}, {...}, ...]
        article_list = response_json.get_articles_list(brand_id=response_json.current_brand['brand_id'],
                                                       group_id=group["group_id"],
                                                       group_count=group['group_count']
                                                    )
        # -- кульбиты с треккингом, есть данные -> вернуть срез, нет -> оставить список артикулов из ответа
        tracking_articles = Tracking.return_articles(article_list)
        if tracking_articles:
            articles = tracking_articles
        else:
            articles = article_list
        # --
        control_counter = 0
        print(f"Обход раздела: {response_json.current_brand['brand_name']}, {group['group_name']}({len(article_list)})")
        for article in articles:
            Tracking.get_article(article)
            control_counter += 1
            # ответ по конкретному артикулу
            article_detail = response_json.get_article_details(brand_id=response_json.current_brand['brand_id'],
                                                               group_id=group["group_id"],
                                                               article_name=article['article_name']
                                                               )
            if article_detail["status"] != 200:
                raise ValueError('article_detail -> response status_code != 200')
            # ответ по связанным ТС с конкретным артикулом, список tecdoc_id_car
            related_vehicles_id = response_json.get_related_vehicles(article['article_id'])
            # сгенерировать итоговый объект по текущему артикулу
            parsing.create_obj_article(article_detail, related_vehicles_id)

        if group['group_count'] != control_counter:
            raise ValueError(f"group['group_count'] != control_counter, {response_json.current_brand['brand_name']}, {group['group_name']}")
        # очистить поле current_article
        Tracking.clear_article()

if __name__ == '__main__':
    main()
