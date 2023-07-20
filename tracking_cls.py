import os
import pickle


class Tracking:
    TRACKING_PATH_DIR = os.path.join(os.getcwd(), 'tracking')
    TRACKING_PATH_FILE_GROUP = os.path.join(TRACKING_PATH_DIR, 'last_group.pickle')
    TRACKING_PATH_FILE_ARTICLE = os.path.join(TRACKING_PATH_DIR, 'last_article.pickle')
    current_group = None
    current_article = None

    @classmethod
    def get_group(cls, current_group):
        cls.current_group = current_group

    @classmethod
    def get_article(cls, current_article):
        cls.current_article = current_article

    @classmethod
    def save(cls):
        if not os.path.exists(cls.TRACKING_PATH_DIR):
            os.mkdir(cls.TRACKING_PATH_DIR)

        with open(cls.TRACKING_PATH_FILE_GROUP, 'wb') as f:
            pickle.dump(cls.current_group, f)
        with open(cls.TRACKING_PATH_FILE_ARTICLE, 'wb') as f:
            pickle.dump(cls.current_article, f)

    @classmethod
    def return_groups(cls, lst):
        if os.path.exists(cls.TRACKING_PATH_FILE_GROUP):
            with open(cls.TRACKING_PATH_FILE_GROUP, 'rb') as f:
                data = pickle.load(f)
            if data:
                # with open(cls.TRACKING_PATH_FILE_GROUP, 'wb') as f:
                #     pickle.dump(None, f)
                return lst[lst.index(data):]
            else:
                return None
        else:
            return None

    @classmethod
    def return_articles(cls, article_list):
        if os.path.exists(cls.TRACKING_PATH_FILE_ARTICLE):
            with open(cls.TRACKING_PATH_FILE_ARTICLE, 'rb') as f:
                data = pickle.load(f)
            # with open(cls.TRACKING_PATH_FILE_ARTICLE, 'wb') as f:
            #     pickle.dump(None, f)
            if data:
                return article_list[article_list.index(data):]
            else:
                return None
        else:
            return None

    @classmethod
    def clear_article(cls):
        if os.path.exists(cls.TRACKING_PATH_FILE_ARTICLE):
            with open(cls.TRACKING_PATH_FILE_ARTICLE, 'wb') as f:
                pickle.dump(None, f)


