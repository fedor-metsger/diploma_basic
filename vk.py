from time import ctime
import requests
from pprint import pprint

class VK:
    """
    Класс для работы с пользователем VK
    """
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        """
        Возвращает информацию о пользователе
        :return:
        """
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id, "fields":"education,sex"}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def search_groups(self, query, sorting=0):
        """
        Производит поиск групп по ключевому слову "query"
        Параметры sort
        0 — сортировать по умолчанию (аналогично результатам поиска в полной версии сайта);
        6 — сортировать по количеству пользователей.
        """
        params = {
            'q': query,
            'access_token': self.token,
            'v': self.version,
            'sort': sorting,
            'count': 300
        }
        req = requests.get('https://api.vk.com/method/groups.search', params).json()
        return req['response']['items']

    def get_followers(self, user_id=None):
        """
        Возвращает список подписчиков
        :param user_id:
        :return:
        """
        followers_params = {
            'count': 1000,
            'user_id': user_id
        }
        res = requests.get(
            "https://api.vk.com/method/users.getFollowers",
            params={**self.params, **followers_params}
        ).json()
        return res['response']

    def get_groups(self, user_id=None):
        """
        Возвращает список групп пользователя
        :param user_id:
        :return:
        """
        groups_params = {
            'count': 1000,
            'user_id': user_id,
            'extended': 1,
            'fields': 'members_count'
        }
        res = requests.get(
            "https://api.vk.com/method/groups.get",
            params={**self.params, **groups_params})
        return res.json()

    def get_news(self, query):
        """
        Выводит последние новости по ключевому слову
        :param query:
        :return:
        """
        groups_params = {
            'q': query,
            'count': 200
        }

        all_res = []
        while True:
            result = requests.get(
                "https://api.vk.com/method/newsfeed.search",
                params={**self.params, **groups_params})
#            time.sleep(0.33)
            all_res.extend(result.json()['response']['items'])
            if 'next_from' in result.json()['response']:
                groups_params['start_from'] = result.json()['response']['next_from']
            else:
                break
        return all_res

    def _is_img_type_better(self, type1, type2):
        """
        Сравнивает типы аватарок. Нужно для того, чтобы выбрать бОльшую по размеру.
        Связано с тем, что иногда VK не возвращает размер фото, и нужно смотреть на тип
        :return:
        """
        types = ['s', 'm', 'o', 'p', 'q', 'r', 'x', 'y', 'z', 'w']

        if type1 in types and type2 in types and types.index(type1) > types.index(type2):
            return False
        return True

    def _add_img_to_dict(self, img_dict, likes, date, url, size):
        """
        Добавляет картинку в словарь. Ключ - количество лайков.
        Если картинка с таким количеством лайков уже есть,
        е качестве ключа используется количество лайков + дата
        :param img_dict:
        :param likes:
        :param date:
        :param url:
        :return:
        """
        filename_extension = url.split('?')[0].split('.')[-1]
#        print(likes, date, url, filename_extension)
        if str(likes) + '.' + filename_extension in img_dict.keys():
            img_dict[str(likes) + '-' + str(date) + '.' + filename_extension] = {"url": url, "size": size}
        else:
            img_dict[str(likes) + '.' + filename_extension] = {"url": url, "size": size}

    def get_photos(self, owner, number=5):
        """
        Возвращает number фото, загруженных пользователем owner
        :param query:
        :return:
        """
        photo_params = {
            "owner_id": owner,
            "album_id": "profile",
            "extended": 1,
            "count": number
        }

        result = requests.get(
            "https://api.vk.com/method/photos.get",
            params={**self.params, **photo_params})
        if result.status_code != 200: return None
        if "response" not in result.json().keys(): return None
#        pprint(type(result.json()))
#        pprint(result.json()["response"])
        img_dict = {}
        for ph in result.json()["response"]["items"]:
#            print(f'Likes:{ph["likes"]["count"]} Date: {ctime(ph["date"])}')
            size, url, img_typ = None, None, None
            for s in ph["sizes"]:
#                print(s["type"], s["height"], s["width"])
                if not url or int(s["height"]) + int(s["width"]) > size or \
                        self._is_img_type_better(img_typ, s["type"]):
                    size = int(s["height"]) + int(s["width"])
                    url = s["url"]
                    img_type = s["type"]
#            print(img_type, size, url)
            self._add_img_to_dict(img_dict, ph["likes"]["count"], ph["date"], url, img_type)
#        print(img_dict)
        return img_dict

    def download_photo(self, file_name, url):
        """
        Скачивает фото с VK
        :return:
        """
        result = requests.get(url)
        if result.status_code != 200:
            return "Ошибка при скачивании файла"

        with open(file_name, "wb") as outf:
            outf.write(result.content)

        return "Файл скачан успешно"
