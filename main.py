
from vk import VK
from yandex import YaUploader
from pprint import pprint

VK_TOKEN_FILE = "vk_token.txt"

def load_vk_token(file_name):
    """
    Загружает токен для работы с VK из файла
    """
    with open(file_name) as inf:
        return inf.readline()

def main():
    """
    main()
    :return:
    """
    vk_token = load_vk_token(VK_TOKEN_FILE)

# Получить id пользователя VK и токен от пользователя Yandex
    user_id = input("Введите id пользователя VK: ")
    ya_token = input("Введите токен от Yandex-Диска: ")

# Получить список аватарок от пользователя VK
    vk = VK(vk_token, user_id)
    # pprint(vk.users_info())
    # pprint(vk.search_groups("python"))
    # pprint(vk.get_followers())
    # pprint(vk.get_groups())
    # pprint(vk.get_news('коронавирус'))
    images = vk.get_photos(user_id)
    if not images or not len(images.keys()):
        print("Не могу загрузить список аватарок из VK")
        return
    else:
        print(f"Получен список из {len(images.keys())} первых аватарок.")

# Скачать аватарки с сайта VK
    for img_name in images.keys():
        print(f'Скачиваю {img_name}, размер {images[img_name]["size"]}, URL: {images[img_name]["url"]}')
        print(vk.download_photo(img_name, images[img_name]["url"]))

# Загрузить аватарки на Яндекс-Диск
    uploader = YaUploader(ya_token)
    dir_name = f"id{user_id}-photos"
    print(f"Аватарки будут загружены на Yandex диск в папку {dir_name}")
    if not uploader.mkfolder(dir_name):
        return

    res_json = []
    for img_name in images.keys():
        print(f'Загружаю файл {img_name}')
        if uploader.upload(img_name, dir_name):
            res_json.append({"file_name": img_name, "size": images[img_name]["size"]})
    print("Результирующий json:")
    pprint(res_json)


if __name__ == "__main__":
    main()