
import json
import requests

BASE_URL = "https://cloud-api.yandex.net/v1/disk/resources"
FILES_URL = "https://cloud-api.yandex.net/v1/disk/resources/files"
UPLOAD_URL = "https://cloud-api.yandex.net/v1/disk/resources/upload"


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": "OAuth {}".format(self.token)
        }

    def get_files_list(self):
        """
        Метод возвращает список файлов на яндекс диске
        """
        headers = self.get_headers()
        response = requests.get(FILES_URL, headers=headers)
        #        print(response.json())
        return response.json()

    def _get_upload_link(self, file_name):
        """
        Метод возвращает ссылку для загрузки файла
        """
        headers = self.get_headers()
        params = {"path": file_name, "overwrite": "true"}
        response = requests.get(UPLOAD_URL, headers=headers, params=params)
        if response.status_code != 200:
            print("Ошибка, status code: " + str(response))
#        else:
#            print("URL для загрузки файла получен успешно")
        return (response.json())

    def upload(self, file_name, dir_name=""):
        """
        Метод загружает файл по имени file_name на яндекс диск
        """
        if dir_name != "": full_name = dir_name + '/' + file_name
        else: full_name = file_name
        href = self._get_upload_link(file_name=full_name).get("href", "")
        if not href:
            print("Oшибка: href == None")
        #        print("href:", href)
            return False
        response = requests.put(href, data=open(file_name, "rb"))
        if response.status_code == 201:
            print("Файл загружен успешно")
            return True
        print("Ошибка, status code: " + str(response))
        return False

    def mkfolder(self, dir_name):
        """
        Метод создаёт папку (каталог) на яндекс диске
        """

        params = {"path": dir_name}
        response = requests.put(BASE_URL, headers=self.get_headers(), params=params)
        if response.status_code == 201:
            print(f"Каталог {dir_name} на Yandex диске создан успешно")
        elif response.status_code == 409:
            print(f"Каталог {dir_name} на Yandex диске уже существует")
        else:
            print("Ошибка, status code: " + str(response))
            return False
        return True